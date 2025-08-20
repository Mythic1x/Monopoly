from abc import ABC
import asyncio
from typing import Self
from websockets.asyncio.server import serve

class LLNode[T]:
    value: T
    next: Self | None
    def __init__(self, value: T, next: Self | None = None):
        self.value = value
        self.next = None

class LinkedList[T]:
    head: LLNode[T] | None
    tail: LLNode[T] | None
    len: int
    def __init__(self):
        self.head = None
        self.tail = None
        self.len = 0

    def append(self, item: T):
        self.len += 1
        if self.head is None:
            self.head = LLNode(item)
            self.tail = self.head
        elif self.tail:
            self.tail.next = LLNode(item)
            self.tail = self.tail.next
        else:
            #this should never happen
            self.tail = LLNode(item)



type spacetype_t = int

class Player:
    ...

class Space(ABC):
    def onland(self, player: Player) -> None:
        pass

class Space_Property(Space):
    cost: int
    

class Board:
    state: LinkedList[Space]
    def __init__(self, *spaces: Space):
        self.state = LinkedList[Space]()
        for space in spaces:
            self.state.append(space)

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
