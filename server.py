import asyncio
from collections.abc import Generator
import importlib.util
import random
import json
import sys

from types import ModuleType
from typing import Any, Callable, Self
from websockets.asyncio.server import ServerConnection, serve
from websockets.legacy.server import WebSocketServerProtocol


from boardbuilder import buildFromFile
from board import Board, Player, Space, status_t, statusreturn_t
from client import Client, WSClient, TermClient
ipConnections: dict[Any, Player] = {}


def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec:
        raise ImportError()
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class Lobby:
    players: list[Player]
    def __init__(self):
        self.players = []

    def join(self, p: Player):
        self.players.append(p)

    async def moveToGame(self, player: Player, game: "Game", onjoin: Callable[[], Any] | None = None):
        if player not in self.players:
            return
        self.players.remove(player)
        response = json.loads(await player.client.read('waiting for details'))
        details = response['details']
        player.name = details['name']
        player.piece = details['piece']
        await player.client.write({"response": "join-game", "value": "join"})
        await game.join(player, onjoin)

class Game:
    board: Board
    #id: Player
    players: dict[str, Player]
    curTurn: int
    dSides: int
    playerTurn: int
    clients: list[Client]

    def __init__(self, boardname: str, dSides: int = 6):
        boardFile = f"./boards/{boardname}.json"
        handlers: dict[str, ModuleType] = {}
        generic_handlers = import_from_path("generic", "./boards/generic.py")
        try:
            handlers[boardname] = import_from_path(boardname, f"./boards/{boardname}.py")
        except Exception as e:
            print(e)
        handlers["generic"] = generic_handlers
        self.board = Board(boardname, handlers, buildFromFile(boardFile))
        self.players = {}
        self.curTurn = 0
        self.dSides = dSides
        self.playerTurn = 1
        self.clients = []

    @property
    def curPlayer(self) -> Player:
        values = list(self.players.values())
        return values[self.curTurn]

    async def join(self, player: Player, onjoin: Callable[[], Any] | None = None):
        self.players[player.id] = player
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
        await self.run(player)

    def endTurn(self):
        self.advanceTurn()

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.players.values())) + 1
        self.curTurn = self.playerTurn - 1

    async def handleAction(self, action: dict[str, Any], player: Player):
        client: Client = player.client
        
        #player-info is for the ui to know who the player is
        #player-list is generally how the ui knows the information about all the players
        #player-info should only be used when the ui is connecting or calling send-player-info

        match action["action"]:

            case "end-turn":
                self.endTurn()
                await self.broadcast({"response": "next-turn", "value": self.curPlayer.toJson()})

            case "send-player-info":
                await client.write({"response": "player-info", "value": player.toJson()})

            case "connect":
                await client.write({"response": "assignment", "value": player.id})
                await self.broadcast({"response": "board", "value": self.board.toJson()})
                await self.broadcast({"response": "next-turn", "value": self.curPlayer.toJson()})
                await client.write({"response": "current-space", "value": player.space.toJson()})
                await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})

            case "teleport":
                spaceId = action["spaceid"]
                playerId = action["playerid"]

                space = self.board.getSpaceById(spaceId)
                if not space:
                    await client.write(client.mknotif(f"invalid space id: {spaceId}"))
                else:
                    for status in self.board.moveTo(self.players[playerId], space):
                        await client.handleStatus(status, player)
                    await self.broadcast({"response": "board", "value": self.board.toJson()})
                    await self.sendUpdatedStateToClient(client, player)

            case "roll":
                for status in self.board.rollPlayer(player, self.dSides):
                    await client.handleStatus(status, player)
                await self.sendUpdatedStateToClient(client, player)

            case "set-details":
                details = action["details"]
                player.name = details["name"]
                player.piece = details["piece"]

            case "request-space":
                await client.write({"response": "current-space", "value": player.space.toJson()})

            case "set-money":
                player.money = int(action["money"])

            case "buy":
                property = self.board.spaces[action["spaceid"]]
                result = player.buy(property)
                await self.broadcastStatus(result, player)
                await self.sendUpdatedStateToClient(client, player)

            case "buy-house":
                property = self.board.spaces[action["spaceid"]]
                result = player.buyHouse(property)
                await self.broadcastStatus(result, player)
                await self.sendUpdatedStateToClient(client, player)

            case "buy-hotel":
                property = self.board.spaces[action["spaceid"]]
                result = player.buyHotel(property)
                await self.broadcastStatus(result, player)
                await self.sendUpdatedStateToClient(client, player)

            case "propose-trade":
                trade = action["trade"]
                to = action["playerid"]
                p = self.players.get(to)
                if not p:
                    await client.write({"response": "notification", "value": "invalid player id"})
                else:
                    await client.write({"response": "trade-proposal", "value": trade})

        await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})

    async def run(self, player: Player):
        async for message in player.client:
            await self.handleAction(message, player)

    async def broadcast(self, message: dict | list[dict]):
        for client in self.clients:
            await client.write(message)

    async def broadcastStatus(self, status: status_t, player: Player):
        for client in self.clients:
            await client.handleStatus(status, player)

    async def sendToClient(client: Client, message: dict):
        client.write(message)

    async def sendUpdatedStateToClient(self, client: Client, player: Player):
            await client.write([
                {"response": "current-space", "value": player.space.toJson()},
                {"response": "assignment", "value": player.id}
            ])
            await self.broadcast([
                {"response": "next-turn", "value": self.curPlayer.toJson()},
                {"response": "board", "value": self.board.toJson()},
                {"response": "player-list", "value": [player.toJson() for player in self.players.values()]}
            ])
            
game = Game("main")
lobby = Lobby()

async def gameServer(ws: ServerConnection):
    c = WSClient(ws)

    if ws.remote_address[0] in ipConnections:
        player = ipConnections[ws.remote_address[0]]
        game.disconnectClient(player.client)
        player.client = c
        await player.client.write({"response": "reconnect", "value": {"name": player.name, "piece": player.piece}})
        await game.rejoin(player)
    else:
        player = Player(str(ws.id), len(game.clients), c)
        lobby.join(player)
        await lobby.moveToGame(player, game, onjoin=lambda: ipConnections.__setitem__(ws.remote_address[0], player))
        

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "t":
        c = TermClient()
        player = Player("1", len(game.clients), c)
        lobby.join(player)
        await lobby.moveToGame(player, game)
    else:
        async with serve(gameServer, "0.0.0.0", 8765) as server:
            await server.serve_forever()

asyncio.run(main())
