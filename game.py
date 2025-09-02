import asyncio
import importlib.util
import json
import os
import sys
import time
from types import ModuleType
from typing import Any, Callable
from board import BANKRUPT, Board, Chance, Player, spacetype_t, status_t
from boardbuilder import buildFromFile
from client import Client

import actions as Actions

def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec:
        raise ImportError()
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class Game:
    board: Board
    #id: Player
    players: dict[str, Player]
    curTurn: int
    dSides: int
    playerTurn: int
    clients: list[Client]
    activeAuction: dict[str, Any] | None
    activePlayers: list[Player]

    def __init__(self, boardname: str, dSides: int = 6):
        boardFile = f"./boards/{boardname}.json"
        handlers: dict[str, ModuleType] = {}
        generic_handlers = import_from_path("generic", "./boards/generic.py")
        try:
            handlers[boardname] = import_from_path(boardname, f"./boards/{boardname}.py")
        except Exception as e:
            print(e)
        handlers["generic"] = generic_handlers

        if os.path.isdir(f"./boards/{boardname}-chance.json"):
            path = f"./boards/{boardname}-chance.json"
        else:
            path = f"./boards/generic-chance.json"
        with open(path) as f:
            cards = [Chance(**v) for v in json.load(f)]
        self.board = Board(boardname, handlers, buildFromFile(boardFile), cards)
        self.players = {}
        self.curTurn = 0
        self.dSides = dSides
        self.playerTurn = 1
        self.clients = []
        self.activeAuction = None
        self.activePlayers = []

    @property
    def curPlayer(self) -> Player:
        values = list(self.activePlayers)
        return values[self.curTurn]

    async def join(self, player: Player, onjoin: Callable[[], Any] | None = None):
        self.players[player.id] = player
        self.activePlayers.append(player)
        self.board.addPlayer(player)
        self.clients.append(player.client)
        if onjoin:
            onjoin()
        await player.client.write({"response": "assignment", "value": player.id})
        await self.broadcast({"response": "board", "value": self.board.toJson()})
        await self.run(player)

    def disconnectClient(self, client: Client):
        self.clients.remove(client)

    async def rejoin(self, player: Player):
        self.clients.append(player.client)
        await player.client.write({"response": "assignment", "value": player.id})
        await self.broadcast({"response": "board", "value": self.board.toJson()})
        await self.broadcast({"response": "next-turn", "value": self.curPlayer.toJson()})
        await player.client.write({"response": "current-space", "value": player.space.toJson()})
        await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})
        print("JOIN", self.activeAuction)
        if self.activeAuction is not None: 
             await self.broadcast({"response": "auction-status", "value": self.activeAuction})
        await self.run(player)

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.activePlayers)) + 1
        self.curTurn = self.playerTurn - 1

    def createAuction(self, forSpace: spacetype_t, end_time=10000, starting_bid=0):
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
            self.players[self.activeAuction["bidder"]].takeOwnership(space, self.activeAuction["current_bid"])
            await self.broadcast([{"response": "auction-end"}, {"response": "board", "value": self.board.toJson()}])
        else:
            await self.broadcast({"response": "auction-end"})
        self.activeAuction = None


    def handleStatus(self, status: status_t):
        if status.broadcast:
            return True, 


    async def handleAction(self, action: dict[str, Any], player: Player):
        client: Client = player.client
        
        #player-info is for the ui to know who the player is
        #player-list is generally how the ui knows the information about all the players
        #player-info should only be used when the ui is connecting or calling send-player-info

        actionFnName = "".join(k.title() if i > 0 else k for i, k in enumerate(action["action"].split("-")))
        if hasattr(Actions, actionFnName):
            if (fn := getattr(Actions, actionFnName)) and callable(fn):
                try:
                    for broadcast, value in fn(self, action, player):
                        if broadcast is True:
                            await self.broadcast(value)
                        elif broadcast is False:
                            await client.write(value)
                        elif isinstance(broadcast, Client):
                            await broadcast.write(value)
                except TypeError as e:
                    print(e)

        await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})

    async def run(self, player: Player):
        async for message in player.client:
            await self.handleAction(message, player)

    async def broadcast(self, message: dict | list[dict]):
        for client in self.clients:
            await client.write(message)

    async def auctionTimer(self):
        while time.time() < self.activeAuction["end_timestamp"] / 1000:
            await asyncio.sleep(1)

        await self.endAuction()
