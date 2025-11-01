import asyncio
import dataclasses
import importlib.util
import json
import os
import random
import sys
import time
import traceback
from types import ModuleType
from typing import Any, Callable
from board import Board, Chance, player_t, spacetype_t, status_t
from loan import Loan
from player import Player
from trade import Trade
from boardbuilder import buildFromFile
from client import Client

import actions as Actions
from gameregistry import addgame, gameid_t

def import_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec:
        raise ImportError()
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader, "spec.loader does not exist, cannot load board and associated data (like chance cards)"
    spec.loader.exec_module(module)
    return module


class Game:
    boards_path: str = "./boards"

    board: Board
    #id: Player
    players: dict[str, Player]
    curTurn: int
    dSides: int
    playerTurn: int
    clients: list[Client]
    activeAuction: dict[str, Any] | None
    activePlayers: list[Player]
    id: gameid_t
    loans: list[Loan]
    trades: list[Trade]
    started: bool
    
    def toJson(self):
        return {
            "started": self.started,
            "host": self.host,
        }

    def __init__(self, boardname: str, dSides: int = 6):
        boardFile = f"{self.boards_path}/{boardname}.json"
        handlers: dict[str, ModuleType] = {}
        generic_handlers = import_from_path("generic", f"{self.boards_path}/generic.py")
        try:
            handlers[boardname] = import_from_path(boardname, f"{self.boards_path}/{boardname}.py")
        except Exception as e:
            print(e)
        handlers["generic"] = generic_handlers

        if os.path.isdir(f"{self.boards_path}/{boardname}-chance.json"):
            path = f"{self.boards_path}/{boardname}-chance.json"
        else:
            path = f"{self.boards_path}/generic-chance.json"
        with open(path) as f:
            cards = [Chance(**v) for v in json.load(f)]

        self.id = random.random()

        addgame(self.id, self)

        self.board = Board(self.id, boardname, handlers, buildFromFile(self.id, boardFile), cards)
        self.players = {}
        self.curTurn = 0
        self.dSides = dSides
        self.playerTurn = 1
        self.clients = []
        self.activeAuction = None
        self.activePlayers = []
        self.loans = []
        self.trades = []
        self.started = False

    @property
    def curPlayer(self) -> Player:
        values = list(self.activePlayers)
        return values[self.curTurn]
    
    @property
    def host(self):
        if not self.started and len(self.activePlayers) > 0:
            return self.activePlayers[0].id
        elif self.started:
            return next(player.id for player in self.activePlayers if player.host)
        return None

    def getplayer(self, id: player_t) -> Player:
        p = self.players.get(id)
        assert p, f"Player@:{id} does not exist"
        return p

    async def join(self, player: Player, onjoin: Callable[[], Any] | None = None):
        self.players[player.id] = player
        self.activePlayers.append(player)
        self.board.addPlayer(player)
        self.clients.append(player.client)
        if onjoin:
            onjoin()
        await player.client.write({"response": "assignment", "value": player.id})
        await self.broadcast({"response": "board", "value": self.board.toJson()})
        await self.broadcast({"response": "lobby-state", "value": self.toJson()})
        await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})
        await self.run(player)

    def disconnectClient(self, client: Client):
        self.clients.remove(client)
        if not self.started:
            client

    async def rejoin(self, player: Player):
        assert player.space, f"{player} is not on a space"
        self.clients.append(player.client)
        await player.client.write({"response": "assignment", "value": player.id})
        await self.broadcast({"response": "board", "value": self.board.toJson()})
        await self.broadcast({"response": "next-turn", "value": self.curPlayer.toJson()})
        await player.client.write({"response": "current-space", "value": player.space.toJson()})
        await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})
        await self.broadcast({"response": "lobby-state", "value": self.toJson()})
        if len(self.loans) > 0:
            await self.broadcast({"response": "loan-list", "value": [loan.toJson() for loan in self.loans]})
        if len(self.trades) > 0:
            await self.broadcast({"response": "loan-list", "value": [trade.toJson() for trade in self.trades]})
        print("JOIN", self.activeAuction)
        if self.activeAuction is not None: 
             await self.broadcast({"response": "auction-status", "value": self.activeAuction})
        await self.run(player)

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.activePlayers)) + 1
        self.curTurn = self.playerTurn - 1

    def createAuction(self, forSpace: spacetype_t, end_time: int=10000, starting_bid: int=0):
        self.activeAuction = {
            "current_bid": starting_bid,
            "bidder": None,
            "end_time": end_time,
            "space": forSpace,
            "end_timestamp": (time.time() * 1000) + end_time
        }        

    def updateAuction(self, **kwargs):
        if not self.activeAuction: return
        for k, v in kwargs.items():
            self.activeAuction[k] = v
        self.activeAuction["end_timestamp"] = self.activeAuction["end_time"] + (time.time() * 1000)

    async def endAuction(self):
        if not self.activeAuction: return
        if self.activeAuction["bidder"]:
            space = self.board.getSpaceById(self.activeAuction["space"])
            assert space, f"Space@:{self.activeAuction["space"]} does not exist"
            self.players[self.activeAuction["bidder"]].takeOwnership(space, self.activeAuction["current_bid"])
            await self.broadcast([{"response": "auction-end"}, {"response": "board", "value": self.board.toJson()}])
        else:
            await self.broadcast({"response": "auction-end"})
            await self.broadcast(Actions.getUpdatedState(self))
        self.activeAuction = None



    async def handleAction(self, action: dict[str, Any], player: Player):
        client: Client = player.client

        #player-info is for the ui to know who the player is
        #player-list is generally how the ui knows the information about all the players
        #player-info should only be used when the ui is connecting or calling send-player-info

        actionFnName = "".join(k.title() if i > 0 else k for i, k in enumerate(action["action"].split("-")))
        if hasattr(Actions, actionFnName):
            if (fn := getattr(Actions, actionFnName)) and callable(fn):
                try:
                    i = fn(self, action, player)
                    if i:
                        for broadcast, value in i:
                            print(f"MESSAGE {actionFnName=} {broadcast=} {value=}")
                            if isinstance(value, status_t):
                                name = value.__class__.__name__
                                value = dataclasses.asdict(value)
                                value["status"] = name.lower().replace("_", "-")
                                value = {"response": "notification", "value": value}
                            if broadcast is True:
                                await self.broadcast(value)
                            elif broadcast is False:
                                await client.write(value)
                            elif isinstance(broadcast, Client):
                                await broadcast.write(value)
                except TypeError as e:
                    print(traceback.format_exc())

        await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})

    async def run(self, player: Player):
        async for message in player.client:
            await self.handleAction(message, player)

    async def broadcast(self, message: dict[Any, Any] | list[dict[Any, Any]]):
        for client in self.clients:
            await client.write(message)

    async def auctionTimer(self):
        assert self.activeAuction, "There is no auction running for auctionTimer to act on"

        while time.time() < self.activeAuction["end_timestamp"] / 1000:
            await asyncio.sleep(1)

        await self.endAuction()