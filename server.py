from abc import ABC
import asyncio
from typing import Self
from websockets.asyncio.server import serve

from player import Player
from board import Board

class Game:
    board: Board
    def __init__(self):
        self.board = Board()


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "0.0.0.0", 8765) as server:
        await server.serve_forever()

asyncio.run(main())
