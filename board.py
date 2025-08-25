from collections.abc import Generator
import json
from typing import Any, Callable, Self
import collections
import random

type status_t = str
S_BUY_FAIL: status_t = "BUY_FAIL"
S_BUY_SUCCESS: status_t = "BUY_SUCCESS"
S_BUY_NEW_SET: status_t = "BUY_NEW_SET"
S_PROMPT_TO_BUY: status_t = "PROMPT_TO_BUY"
S_MONEY_LOST: status_t = "MONEY_LOST"
S_MONEY_GIVEN: status_t = "MONEY_GIVEN"
S_NONE: status_t = "NONE"
S_PAY_OTHER: status_t = "PAY_OTHER"
S_PAY_TAX: status_t = "PAY_TAX"
S_PASS_GO: status_t = "PASS_GO"
S_PAY_JAIL: status_t = "PAY_JAIL"

type statusreturn_t = tuple[status_t, Any]

class Player:
    money: int
    id: str
    playerNumber: int
    ownedSpaces: list["Space"]
    #a list of sets by color
    sets: list[str]
    name: str
    space: "Space"
    piece: str
    lastRoll: int

    inJail: bool
    jailDoublesRemaining: int

    JAIL_DOUBLES_FAIL = 0
    JAIL_DOUBLES_SUCCESS = 1
    JAIL_DOUBLES_FORCE_LEAVE = -1

    def __init__(self, id: str, playerNumber: int, client, money: int = 1500):
        self.money = money
        self.id = id
        self.playerNumber = playerNumber
        self.ownedSpaces = []
        self.name = "Timmy 3 (You were the third Timmy!)"
        #this is PIECE
        self.piece = "PIECE"
        self.client = client
        self.sets = []
        self.lastRoll = 0
        self.inJail = False
        self.jailDoublesRemaining = 3

    def gotoJail(self, jail: "Space"):
        self.jailDoublesRemaining = 3
        self.inJail = True
        self.space = jail

    def leaveJail(self):
        self.inJail = False

    def tryDouble(self, roll1: int, roll2: int):
        """
        returns Player.JAIL_DOUBLES_SUCCESS if the double succeeds
        returns Player.JAIL_DOUBLES_FAIL if the double fails
        returns Player.JAIL_DOUBLES_FORCE_LEAVE if the player must leave jail
        """
        if roll1 == roll2:
            return Player.JAIL_DOUBLES_SUCCESS
        self.jailDoublesRemaining -= 1
        if self.jailDoublesRemaining == 0:
            return Player.JAIL_DOUBLES_FORCE_LEAVE
        return Player.JAIL_DOUBLES_FAIL

    def owns(self, space: "Space"):
        return False if not space.owner else space.owner.id == self.id

    def pay(self, amount: int, other: Self):
        self.money -= amount
        other.money += amount

    def payRent(self, other: Self, space: "Space") -> statusreturn_t:
        amount = space.calculatePropertyRent(self.hasSet(space.color, space.set_size))
        self.pay(amount, other)
        return S_PAY_OTHER, amount, other

    def getUtilities(self):
        return [space for space in self.ownedSpaces if space.spaceType == ST_UTILITY]

    def hasSet(self, color: str, necessaryForSet: int):
        if color in self.sets:
            return True

        count = 0
        for space in self.ownedSpaces:
            if space.color == color:
                count += 1
                if count == necessaryForSet:
                    return True
        return False

    def buy(self, space: "Space"):
        if space.cost > self.money or not space.purchaseable or space.owner:
            return S_BUY_FAIL, space

        self.money -= space.cost
        space.owner = self
        self.ownedSpaces.append(space)

        if space.color not in self.sets and space.set_size and self.hasSet(space.color, space.set_size):
            self.sets.append(space.color)
            return S_BUY_NEW_SET, space

        return S_BUY_SUCCESS, space

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
            "piece": self.piece,
            "space": self.space.id,
            "sets": self.sets,
            "name": self.name,
            "ownedSpaces": [space.id for space in self.ownedSpaces]
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

class SpaceAttr:
    name: str
    default_factory: Callable[[], Any]
    def __init__(self, default_factory: Callable[[], Any]):
        self.name = ""
        self.default_factory = default_factory

    def __set_name__(self, owner, name: str):
        self.name = name

    def __get__(self, obj: "Space", objtype=None):
        if self.name in obj.attrs:
            return obj.attrs[self.name]
        else:
            return self.default_factory()

class Space:
    spaceType: spacetype_t
    next: "Space"
    prev: "Space"
    players: list[Player]
    cost: int
    name: str
    owner: Player | None
    attrs: dict[str, Any]
    id: int

    purchaseable: bool

    houses: int
    hotel: bool

    color = SpaceAttr(str)
    set_size = SpaceAttr(int)

    def __init__(self, spaceType: spacetype_t, cost: int, name: str, purchaseable: bool, **kwargs):
        self.spaceType = spaceType
        self.players = []
        self.cost = cost
        self.name = name
        self.next = None
        self.prev = None
        self.attrs = kwargs
        self.owner = None
        self.id = random.randint(1,10000)

        self.purchaseable = purchaseable

        self.houses = 0
        self.hotel = False

    def __next__(self):
        if self.next == None:
            raise StopIteration
        return self.next

    def __repr__(self):
        return f"(${self.cost} {self.name} + {self.attrs})"

    def calculatePropertyRent(self, set: bool):
        if self.spaceType != ST_PROPERTY:
            return 0
        if not self.hotel:
            match self.houses:
                case 0:
                    if set:
                        return self.attrs["rent"] *2
                    return self.attrs["rent"]
                case n:
                    return self.attrs[f"house{n}"]
        return self.attrs["hotel"]

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
        space = Space(self.spaceType, cost=self.cost, name=self.name, purchaseable=self.purchaseable, **self.attrs)
        space.id = self.id
        return space

    def setNext(self, space: Self):
        self.next = space
        space.prev = self

    def put(self, player: Player):
            self.players.append(player)
            player.space = self

    def onland_goto_jail(self, board: "Board", player: Player):
        jail = board.findJail()
        if jail:
            player.gotoJail(jail)
            yield from board.moveTo(player, jail)

    def onland(self, board: "Board", player: Player) -> Generator[statusreturn_t]:
        print("you landed on " + self.name)

        self.players.append(player)
        player.space = self

        if (onland := self.attrs.get("onland")) and callable(onland := getattr(self, onland)):
            print(self.attrs)
            yield from onland(board, player)
            return

        if self.cost < 0:
            player.money += abs(self.cost)
            yield S_MONEY_GIVEN, abs(self.cost)
            return

        if self.isUnowned() and self.purchaseable:
            yield S_PROMPT_TO_BUY, self
            return

        #we can't check if self.owner here because some spaces
        #such as luxury tax rely on this running to run the onrent_luxurytax function
        if not player.owns(self):
            rent = self.attrs.get("rent")
            if not rent:
                yield S_NONE, None
                return
            rent = str(rent)
            if rent.isnumeric() and self.owner:
                yield player.payRent(self.owner, self)
                return
            elif (fn := getattr(self, rent)) and callable(fn):
                yield fn(player)
                return
        yield S_NONE, None

    def onrent_utility(self, player: Player):
        if self.owner is None or self.owner.id == player.id:
            return S_NONE,
        amount = len(player.getUtilities()) * player.lastRoll
        player.pay(amount, self.owner)
        return S_PAY_OTHER, amount, self.owner

    def onrent_railroad(self, player: Player):
        if self.owner is None :
            return S_NONE,
        owed = {
                0: 0,
                1: 25,
                2: 50,
                3: 100,
                4: 100
        }[self.owner.getOwnedRailroads()]
        if owed:
            player.pay(owed, self.owner)
            return S_PAY_OTHER, owed, self.owner

    def onrent_incometax(self, player: Player):
        player.money -= round(player.money * 0.10)
        return S_PAY_TAX, round(player.money * 0.10), "income"

    def onrent_luxurytax(self, player: Player):
        player.money -= 75
        return S_PAY_TAX, 75, "luxury"

    def onleave(self, player: Player):
        self.players.remove(player)

    def onpass(self, player: Player) -> statusreturn_t:
        if self.spaceType == ST_GO:
            player.money += abs(self.cost)
            return S_PASS_GO, abs(self.cost)
        return S_NONE, None

    def iterSpaces(self):
        #if we start on self, the last item in the list will be self,
        #which is the opposite of what we want
        cur = self.prev
        while (cur := next(cur)) is not self.prev:
            yield cur

    def toJson(self):
        dict = {}
        dict["attrs"] = self.attrs
        for key in self.__dict__:
            if not callable(self.__dict__[key]) and not key.startswith("_"):
                if type(self.__dict__[key]) is Player:
                    dict[key] = self.__dict__[key].id
                    continue
                if type(self.__dict__[key]) is Space:
                    continue
                if key == "players":
                    dict[key] = [player.toJson() for player in self.__dict__[key]]
                    continue
                dict[key] = self.__dict__[key] 
        return dict 


class Board:
    #the board keeps track of only the starting space
    #because the space will point to the next space and so on
    
    startSpace: Space
    playerSpaces: dict[str, Space]
    spaces: dict[str, Space]

    def __init__(self, startSpace: Space):
        self.startSpace = startSpace

        self.playerSpaces = {}
        
        self.spaces = {space.id: space for space in startSpace.iterSpaces()}

    def addPlayer(self, player: Player):
        self.startSpace.put(player)
        self.playerSpaces[player.id] = self.startSpace

    def getSpaceById(self, id: int):
        for space in self.startSpace.iterSpaces():
            if space.id == id:
                return space
        return None

    def findJail(self):
        for space in self.startSpace.iterSpaces():
            if space.spaceType == ST_JAIL:
                return space
        return None

    def moveTo(self, player: Player, space: Space):
        self.playerSpaces[player.id].onleave(player)
        self.playerSpaces[player.id] = space
        yield from space.onland(self, player)

    #rolls the dice for a player
    def rollPlayer(self, player: Player, dSides: int) -> Generator[statusreturn_t]:
        d1 = random.randint(1, dSides)
        d2 = random.randint(1, dSides)
        amount = d1 + d2

        player.lastRoll = amount

        if player.inJail:
            match player.tryDouble(d1, d2):
                case Player.JAIL_DOUBLES_FAIL:
                    return
                case Player.JAIL_DOUBLES_SUCCESS:
                    print("SUCCESS", d1, d2)
                    player.leaveJail()
                    yield S_NONE, None
                case Player.JAIL_DOUBLES_FORCE_LEAVE:
                    player.money -= 50
                    player.leaveJail()
                    yield S_PAY_JAIL, player.space.attrs["bailcost"]

        yield from self.move(player, amount)

    #moves the player DOES NOT ROLL DICE
    def move(self, player: Player, amount: int) -> Generator[statusreturn_t]:
        curSpace = self.playerSpaces[player.id]

        curSpace.onleave(player)
        for i in range(amount):
            curSpace = curSpace.next
            yield curSpace.onpass(player)
        yield from curSpace.onland(self, player)

        self.playerSpaces[player.id] = curSpace

    def toJson(self):
        dict =  {
        "spaces": [ space.toJson() for space in self.startSpace.iterSpaces()],
        "playerSpaces": {k: v.toJson() for k, v in self.playerSpaces.items()}
        }    
        return dict
