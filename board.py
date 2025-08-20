from ast import TypeVar
from typing import Any, Self
from player import Player

type spacetype_t = int

ST_PROPERTY: spacetype_t = 0
ST_UTILITY: spacetype_t = 11
ST_COMMUNITY_CHEST: spacetype_t = 1
ST_CHANCE: spacetype_t = 2
ST_JAIL: spacetype_t = 3
ST_FREE_PARKING: spacetype_t = 4
ST_GOTO_JAIL: spacetype_t = 5
ST_GO: spacetype_t = 6
ST_LUXURY_TAX: spacetype_t = 7
ST_INCOME_TAX: spacetype_t = 8
ST_RAILROAD: spacetype_t = 9
ST_VOID: spacetype_t = 10

class Space:
    spaceType: spacetype_t
    next: "Space"
    prev: "Space"
    players: list[str]
    cost: int
    name: str
    attrs: dict[str, Any]

    def __init__(self, spaceType: spacetype_t, cost: int, name: str, **kwargs):
        self.spaceType = spaceType
        self.players = []
        self.cost = cost
        self.name = name
        self.next = None
        self.prev = None
        self.attrs = kwargs

    def __next__(self):
        if self.next == None:
            raise StopIteration
        return self.next

    def __repr__(self):
        return f"({self.name}${self.cost} + {self.attrs})"

    def print(self, stopat=None):
        print(self)
        if self.next is stopat or not self.next:
            return
        self.next.print(self)

    def getLast(self):
        if self.next is None:
            return self
        return self.next.getLast()

    def isloop(self):
        start = self
        cur = self
        while cur := next(cur):
            if cur is start:
                return True
            if cur is None:
                return False


    def copy(self):
        return Space(self.spaceType, cost=self.cost, name=self.name)

    def setNext(self, space: Self):
        self.next = space
        space.prev = self

    def put(self, player: Player):
            self.players.append(player.id)

    def onland(self, player: Player):
        self.players.append(player.id)
        {
            ST_RAILROAD: onland_railroad,
        }[self.spaceType](self, player)

    def onleave(self, player: Player):
        self.players.remove(player.id)

    def onpass(self, player: Player):
        pass


def onland_railroad(rr: Space, player: Player):
    pass

class Board:
    #the board keeps track of only the starting space
    #because the space will point to the next space and so on
    startSpace: Space
    playerSpaces: dict[str, Space]

    def __init__(self, startSpace: Space):
        self.startSpace = startSpace

        self.playerSpaces = {}

    def addPlayer(self, player: Player):
        self.startSpace.put(player)
        self.playerSpaces[player.id] = self.startSpace

    def moveTo(self, player: Player, space: Space):
        self.playerSpaces[player.id].onleave(player)
        space.onland(player)
        self.playerSpaces[player.id] = space

    def move(self, player: Player, amount: int):
        curSpace = self.playerSpaces[player.id]

        curSpace.onleave(player)
        for i in range(amount):
            curSpace = curSpace.next
            curSpace.onpass(player)
        curSpace.onland(player)

        self.playerSpaces[player.id] = curSpace

        player.go()
