import asyncio
import random
import json
from typing import Any, Self
from websockets.asyncio.server import serve


from boardbuilder import buildFromFile
from board import Board, Player, Space
from client import Client, WSClient, TermClient, action_t

class Game:
    board: Board
    players: list[Player]
    curTurn: int
    dSides: int
    playerTurn: int

    def __init__(self, boardFile: str, dSides: int = 6):
        self.board = Board(buildFromFile(boardFile))
        self.players = []
        self.curTurn = 0
        self.dSides = dSides
        self.playerTurn = 1

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

async def handleAction(client: Client, game: Game, action: dict[str, Any]):
    match action["action"]:
        case "start-turn":
            status, *data = game.startTurn()
            await client.handleStatus(game.curPlayer, status, data)
        case "end-turn":
            game.endTurn()

async def terminalGame():
    c = TermClient()
    g = Game("./boards/main.board")
    p = Player("1", 1, 1500)
    g.playerJoin(p)
    async for message in c:
        await handleAction(c, g, message)

async def gameServer(ws):
    c = WSClient(ws)
    g = Game("./boards/main.board")
    async for message in c:
        await handleAction(c, g, message)

async def main():
    async with serve(gameServer, "0.0.0.0", 8765) as server:
        await server.serve_forever()

asyncio.run(main())
