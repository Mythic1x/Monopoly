import asyncio
import random
import json
import sys

from typing import Any, Self
from websockets.asyncio.server import serve


from boardbuilder import buildFromFile
from board import Board, Player, Space
from client import Client, WSClient, TermClient

class Game:
    board: Board
    players: list[Player]
    curTurn: int
    dSides: int
    playerTurn: int
    client: Client

    def __init__(self, client: Client, boardFile: str, dSides: int = 6):
        self.board = Board(buildFromFile(boardFile))
        self.players = []
        self.curTurn = 0
        self.dSides = dSides
        self.playerTurn = 1
        self.client = client

    @property
    def curPlayer(self):
        return self.players[self.curTurn]

    def playerJoin(self, player: Player):
        self.players.append(player)
        self.board.addPlayer(player)

    def startTurn(self):
        #START STATUS
        roll = random.randint(1, self.dSides)
        status = self.board.move(self.curPlayer, roll)
        return status

    def endTurn(self):
        self.advanceTurn()

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.players)) + 1
        self.curTurn = self.playerTurn - 1

    async def handleAction(self, client: Client, action: dict[str, Any]):
        match action["action"]:
            case "start-turn":
                status, *data = self.startTurn()
                await client.handleStatus(self.curPlayer, status, data)
            case "end-turn":
                self.endTurn()
            case "connect":
                await client.write({"response": "board", "value": self.board.toJson()})

    async def run(self):
        await self.client.write({"hi": "hi"})
        async for message in self.client:
            await self.handleAction(self.client, message)


async def gameServer(ws):
    c = WSClient(ws)
    g = Game(c, "./boards/main.board")
    player = Player("1", 1)
    g.playerJoin(player)
    await g.run()

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
