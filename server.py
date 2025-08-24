import asyncio
import random
import json
import sys

from typing import Any, Self
from websockets.asyncio.server import serve


from boardbuilder import buildFromFile
from board import Board, Player, Space
from client import Client, WSClient, TermClient
clients = {}
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
        return values[self.playerTurn - 1]

    def playerJoin(self, player: Player):
        self.players[player.id] = player
        self.board.addPlayer(player)

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

    async def handleAction(self, client: Client, action: dict[str, Any], player: Player):
        match action["action"]:
            case "start-turn":
                status, *data = self.startTurn()
                await client.handleStatus(self.curPlayer, status, data)
            case "end-turn":
                self.endTurn()
                await client.write({"response": "next-turn", "value": self.curPlayer.toJson()})
            case "connect":
                await client.write({"response": "assignment", "value": player.id})
                await client.write({"response": "board", "value": self.board.toJson()})
                await client.write({"response": "next-turn", "value": self.curPlayer.toJson()})
            case "roll":
                self.board.move(player, random.randint(1,self.dSides))
                await client.write({"response": "current-space", "value": player.space.toJson()})
                await client.write({"response": "board", "value": self.board.toJson()})
            case "set-name":
                player.name = action["name"]
            case "request-space":
                await client.write({"response": "current-space", "value": player.space.toJson()})
            case "buy":
                property = self.board.spaces[action["property"]]
                result = player.buy(property)
                if result:
                    notification = f"You successfully bought{property.name}"
                else:
                    notification = "You failed"
                await client.write({"response": "notification", "value": notification })
                

    async def run(self, client: Client, player: Player):
        async for message in client:
            await self.handleAction(client, message, player)
    async def broadcast(self, message: dict):
        for client in self.clients:
            await client.write(message)
    async def sendToClient(client: Client, message: dict):
        client.write(message)
            
game = Game("./boards/main.board")

async def gameServer(ws: Any):
    c = WSClient(ws)
    player = Player(str(random.randint(1,10000)), len(game.clients))
    game.playerJoin(player)
    game.clients.append(c)
    await game.run(c, player)

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "t":
        c = TermClient()
        g = Game(c, "./boards/main.board")
        player = Player("1", 1)
        g.playerJoin(player)
        await g.run()
    else:
        async with serve(gameServer, "0.0.0.0", 8765) as server:
            await server.serve_forever()

asyncio.run(main())
