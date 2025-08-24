import json
from typing import Any, Self
import collections
import random

        

class Player:
    money: int
    id: str
    playerNumber: int
    ownedSpaces: list["Space"]

    def __init__(self, id: str, playerNumber: int, money: int = 100):
        self.money = money
        self.id = id
        self.playerNumber = playerNumber
        self.ownedSpaces = []

    def owns(self, space: "Space"):
        return False if not space.owner else space.owner.id == self.id

    def pay(self, amount: int, other: Self):
        self.money -= amount
        other.money += amount
    def buy(self, space: "Space"):
        if space.cost > self.money:
            return False
        self.money -= space.cost
        space.owner = self
        self.ownedSpaces.append(space)
        
        
    def getOwnedRailroads(self):
        number = 0
        for space in self.ownedSpaces:
            if space.spaceType == ST_RAILROAD:
                number += 1
        return number
    def toJson(self):
        return {
            "money": self.money,
            "id": self.id,
            "playerNumber": self.playerNumber,
            "ownedSpaces": [space.toJson() for space in self.ownedSpaces]
        }

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
    owner: Player
    setAmount: int
    attrs: dict[str, Any]

    def __init__(self, spaceType: spacetype_t, cost: int, name: str, **kwargs):
        self.spaceType = spaceType
        self.players = []
        self.cost = cost
        self.name = name
        self.next = None
        self.prev = None
        self.attrs = kwargs
        self.owner = None

    def __next__(self):
        if self.next == None:
            raise StopIteration
        return self.next

    def __repr__(self):
        return f"(${self.cost} {self.name} + {self.attrs})"

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
    def isUnowned(self):
        if self.owner is None:
            return True
        return False

    def copy(self):
        return Space(self.spaceType, cost=self.cost, name=self.name)

    def setNext(self, space: Self):
        self.next = space
        space.prev = self

    def put(self, player: Player):
            self.players.append(player.id)

    def onland(self, player: Player):
        print("you landed on " + self.name)
        self.players.append(player.id)
        if self.isUnowned() and self.spaceType == ST_PROPERTY:
            return "PROMPT_TO_BUY", self
        if not player.owns(self):
            rent = self.attrs.get("rent")
            if not rent:
                return "NONE",
            rent = str(rent)
            if rent.isnumeric():
                player.pay(int(rent), self.owner)
            elif (fn := getattr(self, rent)) and callable(fn):
                fn(player)
        return "NONE",


    def onrent_railroad(self, player: Player):
        owed = {
                0: 0,
                1: 25,
                2: 50,
                3: 100,
                4: 100
        }[self.owner.getOwnedRailroads()]
        if owed:
            player.pay(owed, self.owner)

    def onleave(self, player: Player):
        self.players.remove(player.id)

    def onpass(self, player: Player):
        pass
    def iterSpaces(self):
        cur = self
        while (cur := next(cur)) is not self:
            yield cur
    def toJson(self):
        dict = {}
        for key in self.__dict__:
            if not callable(self.__dict__[key]) and not key.startswith("_"):
                if type(self.__dict__[key]) is Player:
                    dict[key] = {"id": self.__dict__[key].id}
                    continue
                if type(self.__dict__[key]) is Space:
                    continue
                dict[key] = self.__dict__[key] 
        return dict 


def onland_railroad(self, rr: Space, player: Player):
    if rr.isUnowned(): 
        #prompt player
        pass
    elif rr.owner is not player:
        self.onrent_railroad(self, player)
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
        status = curSpace.onland(player)

        self.playerSpaces[player.id] = curSpace
        return status
    def toJson(self):
        dict =  {
        "spaces": [ space.toJson() for space in self.startSpace.iterSpaces()],
        "playerSpaces": {k: v.toJson() for k, v in self.playerSpaces.items()}
        }    
        return dict
