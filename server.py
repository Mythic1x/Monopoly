from abc import ABC
import asyncio
import random
from typing import Self
from websockets.asyncio.server import serve

from boardbuilder import buildFromFile
from player import Player
from board import Board

class Game:
    board: Board
    players: list[Player]
    curTurn: int

    def __init__(self, boardFile: str):
        self.board = Board(buildFromFile(boardFile))
        self.players = []
        self.curTurn = 0

    def playerJoin(self, player: Player):
        self.players.append(player)
        self.board.addPlayer(player)

    def nextTurn(self):
        roll = random.randint(1, 12)
        self.board.move(self.players[self.curTurn], roll)
        self.curTurn += 1
        if self.curTurn >= len(self.players):
            self.curTurn = 0

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "0.0.0.0", 8765) as server:
        await server.serve_forever()

asyncio.run(main())
