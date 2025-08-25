import asyncio
import random
import json
import sys

from typing import Any, Self
from websockets.asyncio.server import ServerConnection, serve
from websockets.legacy.server import WebSocketServerProtocol


from boardbuilder import buildFromFile
from board import S_BUY_NEW_SET, S_BUY_SUCCESS, S_BUY_FAIL, Board, Player, Space
from client import Client, WSClient, TermClient
ipConnections: dict[Any, Player] = {}

class Lobby:
    players: list[Player]
    def __init__(self):
        self.players = []

    def join(self, p: Player):
        self.players.append(p)

    async def moveToGame(self, player: Player, game: "Game"):
        if player not in self.players:
            return
        self.players.remove(player)
        response = json.loads(await player.client.read('waiting for details'))
        details = response['details']
        player.name = details['name']
        player.piece = details['piece']
        await player.client.write({"response": "join-game", "value": "join"})
        await game.join(player)

class Game:
    board: Board
    players: dict[str, Player]
    curTurn: int
    dSides: int
    playerTurn: int
    clients: list[Client]

    def __init__(self, boardFile: str, dSides: int = 6):
        self.board = Board(buildFromFile(boardFile))
        self.players = {}
        self.curTurn = 0
        self.dSides = dSides
        self.playerTurn = 1
        self.clients = []

    @property
    def curPlayer(self) -> Player:
        values = list(self.players.values())
        return values[self.curTurn]

    async def join(self, player: Player):
        self.players[player.id] = player
        self.board.addPlayer(player)
        self.clients.append(player.client)
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

    def startTurn(self):
        #START STATUS
        roll = random.randint(2, self.dSides * 2)
        status = self.board.move(self.curPlayer, roll)
        return status

    def endTurn(self):
        self.advanceTurn()

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.players.values())) + 1
        self.curTurn = self.playerTurn - 1

    async def handleAction(self, action: dict[str, Any], player: Player):
        client: Client = player.client
        match action["action"]:
            case "start-turn":
                status, *data = self.startTurn()
                await self.broadcast({"response": "player-list", "value": [player.toJson() for player in self.players.values()]})
                await client.handleStatus(status, self.curPlayer, data)
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

            case "roll":
                status, *data = self.board.rollPlayer(player, self.dSides)
                await client.write({"response": "current-space", "value": player.space.toJson()})
                await self.broadcast({"response": "board", "value": self.board.toJson()})
                await client.handleStatus(status, player, data)

            case "set-details":
                details = action["details"]
                player.name = details["name"]
                player.piece = details["piece"]

            case "request-space":
                await client.write({"response": "current-space", "value": player.space.toJson()})

            case "buy":
                property = self.board.spaces[action["property"]]
                result, *data = player.buy(property)
                await self.broadcastStatus(result, player, data)
                await self.broadcast({"response": "board", "value": self.board.toJson()})

    async def run(self, player: Player):
        print(player.name)
        async for message in player.client:
            await self.handleAction(message, player)

    async def broadcast(self, message: dict):
        for client in self.clients:
            await client.write(message)
    async def broadcastStatus(self, status, player: Player, data: list[Any]):
        for client in self.clients:
            await client.handleStatus(status, player, data)

    async def sendToClient(client: Client, message: dict):
        client.write(message)
            
game = Game("./boards/main.board")
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
        ipConnections[ws.remote_address[0]] = player
        lobby.join(player)
        await lobby.moveToGame(player, game)

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
