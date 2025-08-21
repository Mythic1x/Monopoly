from abc import ABC
import asyncio
import random
from typing import Any, Self


from boardbuilder import buildFromFile
from board import Board, Player, Space
from statushandler import StatusHandler

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

    def startTurn(self):
        #START STATUS
        roll = random.randint(1, self.dSides)
        status = self.board.move(self.players[self.curTurn], roll)
        return status
    def endTurn(self):
        self.curTurn += 1
        if self.curTurn >= len(self.players):
            self.curTurn = 0
        self.advanceTurn()

    def advanceTurn(self):
        self.playerTurn = (self.playerTurn % len(self.players)) + 1
    def run(self):
        while True:
            curPlayer = self.players[self.curTurn]
            print(f"Player {self.playerTurn} go")
            input()
            status, *data = self.startTurn()
            self.handleStatus(status, data, curPlayer)
            pass
    def handleStatus(self, status: str, data: list[Any], player: Player):
        getattr(StatusHandler, status)(player, *data)
        pass
async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "0.0.0.0", 8765) as server:
        await server.serve_forever()

#asyncio.run(main())
player = Player("1", 1, 1500)
game = Game("./boards/main.board")
game.playerJoin(player)
game.playerJoin(player)
game.run()



