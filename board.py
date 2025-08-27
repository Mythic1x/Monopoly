from collections.abc import Generator
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Self
import time
import random

class status_t:
    broadcast: bool = False

@dataclass
class BUY_FAIL(status_t):
    space: "Space"

@dataclass
class BUY_HOUSE_FAIL(status_t):
    space: "Space"

@dataclass
class BUY_HOTEL_FAIL(status_t):
    space: "Space"

@dataclass
class BUY_SUCCESS(status_t):
    space: "Space"

@dataclass
class BUY_HOUSE_SUCCESS(status_t):
    space: "Space"
    broadcast: bool = True

@dataclass
class BUY_HOTEL_SUCCESS(status_t):
    space: "Space"
    broadcast: bool = True

@dataclass
class BUY_NEW_SET(status_t):
    space: "Space"
    broadcast: bool = True

@dataclass
class PROMPT_TO_BUY(status_t):
    space: "Space"

@dataclass
class MONEY_LOST(status_t):
    amount: int
    broadcast: bool = True

@dataclass
class MONEY_GIVEN(status_t):
    amount: int
    broadcast: bool = True
    
@dataclass 
class AUCTION_END(status_t):
    space: "Space"
    auction_dict: dict
    broadcast: bool = True

@dataclass
class NONE(status_t):
    pass

@dataclass
class PAY_OTHER(status_t):
    amount: int
    payer: "Player"
    other: "Player"
    broadcast: bool = True

@dataclass
class PAY_TAX(status_t):
    amount: int
    taxname: str
    broadcast: bool = True

@dataclass
class PASS_GO(status_t):
    earned: int
    broadcast: bool = True

@dataclass
class PAY_JAIL(status_t):
    cost: int
    broadcast: bool = True


type statusreturn_t = status_t

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

    def trade(self, board: "Board", other: Self, trade: dict[str, Any]):
        for id in trade["give"].get("properties", []):
            space = board.getSpaceById(id)
            if not space or space in other.ownedSpaces:
                continue
            other.ownedSpaces.append(space)
            self.ownedSpaces.remove(space)

        if a := trade["give"].get("money"):
            other.money += a
            self.money -= a

        for id in trade["want"].get("properties", []):
            space = board.getSpaceById(id)
            if not space or space in self.ownedSpaces:
                continue
            other.ownedSpaces.remove(space)
            self.ownedSpaces.append(space)

        if a := trade["want"].get("money"):
            other.money -= a
            self.money += a

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
        return PAY_OTHER(amount, self, other)

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
            return BUY_FAIL(space)

        self.money -= space.cost
        space.owner = self
        self.ownedSpaces.append(space)

        if space.color not in self.sets and space.set_size and self.hasSet(space.color, space.set_size):
            self.sets.append(space.color)
            return BUY_NEW_SET(space)

        return BUY_SUCCESS(space)
    def buyHouse(self, space: "Space"):
        if not self.canBuyHouse(space):
            return BUY_HOUSE_FAIL(space)
        
        self.money -= space.house_cost
        space.houses += 1
        return BUY_HOUSE_SUCCESS(space)
    
    def buyHotel(self, space: "Space"):
        if not self.canBuyHotel(space):
            return BUY_HOTEL_FAIL(space)
        
        self.money -= space.house_cost
        space.hotel = True
        return BUY_HOTEL_SUCCESS(space)
        
    def canBuyHouse(self, space: "Space"):
        if space.color not in self.sets:
            return False
      
        if self.money < space.house_cost:
            return False
       
        if space.houses == 4:
            return False
        
        set_spaces = [s for s in self.ownedSpaces if s.color == space.color]
        for player_space in set_spaces:
            if space.houses > player_space.houses:
                return False
            
        return True
    def canBuyHotel(self, space: "Space"):
        if self.money < space.house_cost:
            return False
        
        if space.houses < 4:
            return False
        
        set_spaces = [s for s in self.ownedSpaces if s.color == space.color]
        for player_space in set_spaces:
            if player_space.houses < 4:
                return False
            
        return True


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
            "ownedSpaces": [space.toJsonForPlayer() for space in self.ownedSpaces]
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
    house_cost = SpaceAttr(int)
    hotel_cost = SpaceAttr(int)
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

    def copy(self, withId = False):
        space = Space(self.spaceType, cost=self.cost, name=self.name, purchaseable=self.purchaseable, **self.attrs)
        if withId:
            space.id = self.id
        return space

    def setNext(self, space: Self):
        self.next = space
        space.prev = self

    def put(self, player: Player):
            self.players.append(player)
            player.space = self

    def onland(self, player: Player) -> Generator[statusreturn_t]:
        self.players.append(player)
        player.space = self
        yield NONE()

    def onleave(self, player: Player):
        self.players.remove(player)
        yield NONE()

    def onpass(self, player: Player) -> Generator[statusreturn_t]:
        yield NONE()
    #auction_time is in milliseconds
    def auction(self, auction_time: int, players: dict[str, Player]):
        auction_dict = {
            "current_bid": 0,
            "bidder": None,
            "end_time": auction_time,
            "space": self.id
        }
        
        while True:
            new_bid = yield auction_dict
            if new_bid:
                player, bid_amount = new_bid
                if player == "END":
                    break
                auction_dict["bidder"] = player.id
                auction_dict["current_bid"] = bid_amount
                auction_dict["end_time"] += 1000
                
        winner = players.get(auction_dict["bidder"])
        if winner is not None:
            winner.money -= auction_dict['current_bid']
            self.owner = winner

        return AUCTION_END(self, winner) 

    def iterSpaces(self):
        #if we start on self, the last item in the list will be self,
        #which is the opposite of what we want
        cur = self
        yield self
        while (cur := next(cur)) is not self:
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
    def toJsonForPlayer(self):
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
                    continue
                dict[key] = self.__dict__[key] 
        return dict 


class Board:
    #the board keeps track of only the starting space
    #because the space will point to the next space and so on
    
    startSpace: Space
    playerSpaces: dict[str, Space]
    spaces: dict[int, Space]

    eventHandlers: dict[str, ModuleType]
    boardName: str

    def __init__(self, name: str, eventHandlers: dict[str, ModuleType], startSpace: Space):
        self.startSpace = startSpace

        self.playerSpaces = {}
        
        self.spaces = {space.id: space for space in startSpace.iterSpaces()}

        self.eventHandlers = eventHandlers
        self.boardName = name

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
        yield from self.runevent("onleave", self.playerSpaces[player.id], player)
        self.playerSpaces[player.id] = space
        yield from self.runevent("onland", space, player)

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
                    yield NONE()
                case Player.JAIL_DOUBLES_FORCE_LEAVE:
                    jail = player.space
                    bail = player.space.attrs["bailcost"]

                    if jail.owner:
                        player.pay(bail, jail.owner)
                    else:
                        player.money -= bail

                    player.leaveJail()

                    yield PAY_JAIL(player.space.attrs["bailcost"])

        yield from self.move(player, amount)

    #call order  using an example event: onland
    #space.onland (DOES NOT STOP HERE)
    #<board-name>.onland_<space-name>()
    #<generic>.onland_<spae-name>()
    #<board-name>.onland()
    #<generic>.onland()
    def runevent(self, name: str, space: Space, player: Player):
        if hasattr(space, name):
            yield from getattr(space, name)(player)

        for fn in (f"{name}_{space.name.replace(" ", "_").lower()}", name):
            print(fn)
            if hasattr(self.eventHandlers.get(self.boardName), fn):
                yield from getattr(self.eventHandlers[self.boardName], fn)(self, space, player)
                return
            elif hasattr(self.eventHandlers["generic"], fn):
                yield from getattr(self.eventHandlers["generic"], fn)(self, space, player)
                return


    #moves the player DOES NOT ROLL DICE
    def move(self, player: Player, amount: int) -> Generator[statusreturn_t]:
        curSpace = self.playerSpaces[player.id]

        yield from self.runevent("onleave", curSpace, player)
        for i in range(amount):
            curSpace = curSpace.next
            yield from self.runevent("onpass", curSpace, player)

        self.playerSpaces[player.id] = curSpace

        yield from self.runevent("onland", curSpace, player)

    def toJson(self):
        dict =  {
        "spaces": [ space.toJson() for space in self.startSpace.iterSpaces()],
        "playerSpaces": {k: v.toJson() for k, v in self.playerSpaces.items()}
        }    
        return dict
