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

ST_PROPERTY: spacetype_t = 0
ST_COMMUNITY_CHEST: spacetype_t = 1
ST_CHANCE: spacetype_t = 2
ST_JAIL: spacetype_t = 3
ST_FREE_PARKING: spacetype_t = 4
ST_GOTO_JAIL: spacetype_t = 5
ST_GO: spacetype_t = 6
ST_LUXURY_TAX: spacetype_t = 7
ST_INCOME_TAX: spacetype_t = 8
ST_RAILROAD: spacetype_t = 9

class Player:
    ...

class Space:
    spaceType: spacetype_t
    def __init__(self, spaceType: spacetype_t, *, cost: int, name: str):
        self.spaceType = spaceType

    def onland(self, player: Player):
        {
            ST_RAILROAD: onland_railroad,
        }[self.spaceType](self, player)

def onland_railroad(rr: Space, player: Player):
    pass


Space(ST_RAILROAD, cost=100, name="pennsylvania ave")

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
