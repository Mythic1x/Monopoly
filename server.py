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
        client = player.client
        match action["action"]:
            case "start-turn":
                status, *data = self.startTurn()
                await client.handleStatus(self.curPlayer, status, data)
            case "end-turn":
                self.endTurn()
                await self.broadcast({"response": "next-turn", "value": self.curPlayer.toJson()})
            case "connect":
                await client.write({"response": "assignment", "value": player.id})
                await self.broadcast({"response": "board", "value": self.board.toJson()})
                await self.broadcast({"response": "next-turn", "value": self.curPlayer.toJson()})
            case "roll":
                status, *data = self.board.rollPlayer(player, self.dSides)
                await client.handleStatus(player, status, data)
                await client.write({"response": "current-space", "value": player.space.toJson()})
                await self.broadcast({"response": "board", "value": self.board.toJson()})
            case "set-name":
                player.name = action["name"]
            case "request-space":
                await client.write({"response": "current-space", "value": player.space.toJson()})
            case "buy":
                property = self.board.spaces[action["property"]]
                result = player.buy(property)
                if result == S_BUY_SUCCESS:
                    notification = f"You successfully bought {property.name}"
                elif result == S_BUY_FAIL:
                    notification = "You failed"
                else:
                    notification = f"You successfully bought {property.name} for a complete set!"
                    await self.broadcast({"response": "new-set", "value": f"{property.color};{player.name}"})
                await client.write({"response": "notification", "value": notification })
                

    async def run(self, player: Player):
        async for message in player.client:
            await self.handleAction(message, player)

    async def broadcast(self, message: dict):
        for client in self.clients:
            await client.write(message)
    async def sendToClient(client: Client, message: dict):
        client.write(message)
            
game = Game("./boards/main.board")

async def gameServer(ws: ServerConnection):
    c = WSClient(ws)

    if ws.remote_address in ipConnections:
        player = ipConnections[ws.remote_address]
    else:
        player = Player(str(ws.id), len(game.clients), c)
        await game.join(player)
    await game.run(player)

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "t":
        c = TermClient()
        player = Player("1", 1, c)
        await game.join(player)
        await game.run(player)
    else:
        async with serve(gameServer, "0.0.0.0", 8765) as server:
            await server.serve_forever()

asyncio.run(main())
