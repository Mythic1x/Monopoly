from abc import ABC
import asyncio
import random
from typing import Self
from websockets.asyncio.server import serve

from boardbuilder import buildFromFile
from board import Board, Player

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

    def playerJoin(self, player: Player):
        self.players.append(player)
        self.board.addPlayer(player)

    def nextTurn(self) -> int:
        roll = random.randint(1, self.dSides)
        self.board.move(self.players[self.curTurn], roll)
        self.curTurn += 1
        if self.curTurn >= len(self.players):
            self.curTurn = 0
        return self.playerTurn

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.players)) + 1

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "0.0.0.0", 8765) as server:
        await server.serve_forever()

asyncio.run(main())
