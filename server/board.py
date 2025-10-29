from collections.abc import Generator
import re
from types import ModuleType
from typing import Any, Callable, Self, TYPE_CHECKING
import random

from monopolytypes import *
from status import *

if TYPE_CHECKING:
    from player import Player

type statusreturn_t = status_t

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


def str2spacetype(str: str):
    return {
        "property": ST_PROPERTY,
        "utility": ST_UTILITY,
        "community_chest": ST_COMMUNITY_CHEST,
        "chance": ST_CHANCE,
        "jail": ST_JAIL,
        "free_parking": ST_FREE_PARKING,
        "goto_jail": ST_GOTO_JAIL,
        "go": ST_GO,
        "luxury_tax": ST_LUXURY_TAX,
        "income_tax": ST_INCOME_TAX,
        "railroad": ST_RAILROAD,
        "void": ST_VOID,
    }[str.lower()]


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
    next: "Space | None"
    prev: "Space | None"
    players: list["Player"]
    cost: int
    name: str
    owner: "Player | None"
    attrs: dict[str, Any]
    id: int
    house_cost: SpaceAttr = SpaceAttr(int)
    hotel_cost: SpaceAttr = SpaceAttr(int)
    purchaseable: bool
    houses: int
    hotel: bool
    color: SpaceAttr = SpaceAttr(str)
    set_size: SpaceAttr = SpaceAttr(int)
    mortgaged: bool

    gameId: float

    def __init__(
        self,
        gameid: float,
        spaceType: spacetype_t,
        cost: int,
        name: str,
        purchaseable: bool,
        **kwargs,
    ):
        self.spaceType = spaceType
        self.players = []
        self.cost = cost
        self.name = name
        self.next = None
        self.prev = None
        self.mortgaged = False
        self.attrs = kwargs
        self.owner = None
        self.id = random.randint(1, 10000)

        self.gameId = gameid

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
        if self.spaceType != ST_PROPERTY or self.mortgaged is True:
            return 0
        if not self.hotel:
            match self.houses:
                case 0:
                    if set:
                        return self.attrs["rent"] * 2
                    return self.attrs["rent"]
                case n:
                    return self.attrs[f"house{n}"]
        return self.attrs["hotel"]

    def print(self, stopat: "Space | None"=None):
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

    def copy(self, withId: space_t | bool=False):
        space = Space(
            self.gameId,
            self.spaceType,
            cost=self.cost,
            name=self.name,
            purchaseable=self.purchaseable,
            **self.attrs,
        )
        if withId:
            space.id = self.id
        return space

    def setNext(self, space: Self):
        self.next = space
        space.prev = self

    def trynext(self):
        assert self.next, "The board is not circular"
        return self.next

    def tryprev(self):
        assert self.prev, "The board is not circular"
        return self.prev


    def put(self, player: "Player"):
        self.players.append(player)
        player.space = self

    def onland(self, player: "Player") -> Generator[statusreturn_t]:
        self.players.append(player)
        player.space = self
        yield NONE()

    def onleave(self, player: "Player"):
        self.players.remove(player)
        yield NONE()

    def onpass(self, player: "Player") -> Generator[statusreturn_t]:
        yield NONE()

    def iterSpaces(self):
        # if we start on self, the last item in the list will be self,
        # which is the opposite of what we want
        cur = self
        yield self
        while (cur := next(cur)) is not self:
            yield cur

    def toJson(self):
        dict = {}
        dict["attrs"] = self.attrs
        for key in self.__dict__:
            if not callable(self.__dict__[key]) and not key.startswith("_"):
                if self.__dict__[key].__class__.__name__ == "Player":
                    dict[key] = self.__dict__[key].id
                    continue
                if type(self.__dict__[key]) is Space:
                    continue
                if key == "players":
                    dict[key] = [player.toJson() for player in self.__dict__[key]]
                    continue
                dict[key] = self.__dict__[key]
        return dict

    def toJsonForPlayer(self):
        dict = {}
        dict["attrs"] = self.attrs
        for key in self.__dict__:
            if not callable(self.__dict__[key]) and not key.startswith("_"):
                if self.__dict__[key].__class__.__name__ == "Player":
                    dict[key] = self.__dict__[key].id
                    continue
                if type(self.__dict__[key]) is Space:
                    continue
                if key == "players":
                    continue
                dict[key] = self.__dict__[key]
        return dict


class Board:
    # the board keeps track of only the starting space
    # because the space will point to the next space and so on

    startSpace: Space
    playerSpaces: dict[player_t, Space]
    players: dict[player_t, "Player"]
    spaces: dict[int, Space]

    eventHandlers: dict[str, ModuleType]
    boardName: str

    chanceCards: list[Chance]

    gameId: float

    def __init__(
        self,
        gameid: float,
        name: str,
        eventHandlers: dict[str, ModuleType],
        startSpace: Space,
        chanceCards: list[Chance],
    ):
        self.startSpace = startSpace

        self.playerSpaces = {}
        self.players = {}

        self.gameId = gameid

        self.spaces = {space.id: space for space in startSpace.iterSpaces()}

        self.eventHandlers = eventHandlers
        self.boardName = name

        self.chanceCards = chanceCards

    def drawChance(self, player: "Player"):
        if self.chanceCards:
            return random.choice(self.chanceCards)
        return Chance("None", "gain", 0)

    def executeChanceCard(self, player: "Player", card: Chance):
        match card.type:
            case "move":
                amount = int(card.data)
                yield from self.move(player, amount)
            case "steal-all":
                amount = int(card.data)
                for p in self.players.values():
                    if p.id == player.id:
                        continue
                    p.pay(amount, player)
            case "gain":
                player.gain(int(card.data))
            case "give-all":
                amount = int(card.data)
                for p in self.players.values():
                    if p.id == player.id:
                        continue
                    player.pay(amount, p)
            case "lose":
                player.money -= int(card.data)
            case "teleport":
                spaceName = card.data.lower().strip()
                pickedSpace = False
                if not self.isValidSpaceName(spaceName):
                    return
                if match := re.match(r"n=(\d+)", spaceName):
                    n = int(match.group(1))
                    spaceName = spaceName.replace(match.group(0), "").strip()
                elif spaceName == "_random":
                    pickedSpace = True
                    n = 0
                    space = random.choice(list(self.spaces.values()))
                else:
                    n = 1
                if not pickedSpace:
                    space = self.getSpaceByName(spaceName, n)
                yield from self.moveTo(player, space)
            case "teleport-next-type":
                ty = str2spacetype(card.data)

                assert player.space, "Player is not on a space?"

                for space in player.space.trynext().iterSpaces():
                    if space.spaceType == ty:
                        yield from self.moveTo(player, space)
                        break

    def isValidSpaceName(self, name: str):
        for space in self.startSpace.iterSpaces():
            if space.name.lower() == name.lower():
                return True

    def addPlayer(self, player: "Player"):
        self.startSpace.put(player)
        self.players[player.id] = player
        self.playerSpaces[player.id] = self.startSpace

    def getSpaceById(self, id: int):
        for space in self.startSpace.iterSpaces():
            if space.id == id:
                return space
        return None

    def getSpaceByName(self, name: str, count: int = 1):
        curSpace = self.startSpace
        nth = 0
        name = name.lower()
        while nth < count:
            if curSpace.name.lower():
                nth += 1
            curSpace = next(curSpace)
        return curSpace.prev

    def findJail(self):
        for space in self.startSpace.iterSpaces():
            if space.spaceType == ST_JAIL:
                return space
        return None

    def moveTo(self, player: "Player", space: Space):
        yield from self.runevent("onleave", self.playerSpaces[player.id], player)
        self.playerSpaces[player.id] = space
        yield from self.runevent("onland", space, player)

    # rolls the dice for a player
    def rollPlayer(self, player: "Player", dSides: int) -> Generator[statusreturn_t]:
        d1 = random.randint(1, dSides)
        d2 = random.randint(1, dSides)
        amount = d1 + d2

        player.lastRoll = amount

        player.compoundLoans()
        for dueLoan in player.incLoanDeadline():
            player.payLoan(dueLoan, dueLoan.totalOwed)
            player.creditScore -= 100
            yield DUE_LOAN(dueLoan.id, player.id)

        assert player.space, "Player is not on a space"
        yield from self.runevent("onroll", player.space, player, amount, d1, d2)

    # call order  using an example event: onland
    # space.onland (DOES NOT STOP HERE)
    # <board-name>.onland_<space-name>()
    # <generic>.onland_<spae-name>()
    # <board-name>.onland()
    # <generic>.onland()
    def runevent(self, name: str, space: Space, player: "Player", *args: Any):
        if hasattr(space, name):
            yield from getattr(space, name)(player, *args)

        for fn in (f"{name}_{space.name.replace(" ", "_").lower()}", name):
            if hasattr(self.eventHandlers.get(self.boardName), fn):
                yield from getattr(self.eventHandlers[self.boardName], fn)(
                    self, space, player, *args
                )
                return
            elif hasattr(self.eventHandlers["generic"], fn):
                yield from getattr(self.eventHandlers["generic"], fn)(
                    self, space, player, *args
                )
                return

    # moves the player DOES NOT ROLL DICE
    def move(self, player: "Player", amount: int) -> Generator[statusreturn_t]:
        curSpace = self.playerSpaces[player.id]

        yield from self.runevent("onleave", curSpace, player)
        for i in range(amount):
            if amount > 0:
                curSpace = curSpace.trynext()
            else:
                curSpace = curSpace.tryprev()
            yield from self.runevent("onpass", curSpace, player)

        self.playerSpaces[player.id] = curSpace

        yield from self.runevent("onland", curSpace, player)

    def toJson(self):
        dict = {
            "spaces": [space.toJson() for space in self.startSpace.iterSpaces()],
            "playerSpaces": {k: v.toJson() for k, v in self.playerSpaces.items()},
        }
        return dict
