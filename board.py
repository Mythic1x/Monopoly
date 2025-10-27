from collections.abc import Generator
from dataclasses import dataclass
import json
import re
from types import ModuleType
from typing import Any, Callable, Self
import random


type player_t = str
type space_t = int
type loan_t = float

class status_t:
    broadcast: bool = False

@dataclass
class DUE_LOAN(status_t):
    loan: loan_t
    player: player_t

@dataclass
class BANKRUPT(status_t):
    player: player_t

@dataclass
class DRAW_CHANCE(status_t):
    event: str
    player: player_t
    
@dataclass
class FAIL(status_t):
    player: player_t
    
@dataclass 
class MORTGAGE_SUCCESS(status_t):
    player: player_t
    space: space_t
    
@dataclass 
class UNMORTGAGE_SUCCESS(status_t):
    player: player_t
    space: space_t

@dataclass
class BUY_FAIL(status_t):
    space: space_t

@dataclass
class BUY_HOUSE_FAIL(status_t):
    space: space_t

@dataclass
class BUY_HOTEL_FAIL(status_t):
    space: space_t

@dataclass
class BUY_SUCCESS(status_t):
    space: space_t

@dataclass
class BUY_HOUSE_SUCCESS(status_t):
    space: space_t
    broadcast: bool = True

@dataclass
class BUY_HOTEL_SUCCESS(status_t):
    space: space_t
    broadcast: bool = True

@dataclass
class BUY_NEW_SET(status_t):
    space: space_t
    broadcast: bool = True

@dataclass
class PROMPT_TO_BUY(status_t):
    space: space_t

@dataclass
class MONEY_LOST(status_t):
    #FIXME this needs a player so that the ui can say which player lost money lmfao
    amount: int
    broadcast: bool = True

@dataclass
class MONEY_GIVEN(status_t):
    amount: int
    broadcast: bool = True
    
@dataclass 
class AUCTION_END(status_t):
    space: space_t
    auction_dict: dict
    broadcast: bool = True

@dataclass
class NONE(status_t):
    pass

@dataclass
class PAY_OTHER(status_t):
    amount: int
    payer: player_t
    other: player_t
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


@dataclass
class Chance:
    event: str
    type: str
    data: Any

type statusreturn_t = status_t

class Loan:
    id: float
    type: str #deadline | per-turn
    amountPerTurn: int
    deadline: int
    amount: int
    interest: int
    interestType: str #simple | compound

    turnsPassed: int

    totalOwed: int
    loaner: "Player | None" #None means bank
    loanee: "Player"

    def __init__(self, loaner, loanee, type: str, amount: int, interest: int, interestType: str, amountPerTurn: int = 0, deadline: int = 0) -> None:
        self.id = random.random()
        self.type = type
        self.amount = amount
        self.interest = interest
        self.interestType =interestType

        self.amountPerTurn = amountPerTurn
        self.deadline = deadline

        self.turnsPassed = 0

        self.loaner = loaner
        self.loanee = loanee

        self.totalOwed = amount
        if self.type == 'simple':
            self.totalOwed = round(self.totalOwed * (1 + (interest / 100)))

    def compound(self):
        if self.interestType == 'simple': return
        self.totalOwed = round(self.totalOwed * (1 + (self.interest / 100)))

    def payTurnAmount(self):
        self.totalOwed -= self.amountPerTurn
        if self.loaner:
            self.loaner.money += self.amountPerTurn
        self.loanee.money -= self.amountPerTurn
        return self.amountPerTurn

    def payAmount(self, amount: int):
        if self.loaner:
            self.loaner.money += amount
        self.loanee.money -= amount
        self.totalOwed -= amount

    def toJson(self):
        return {
            "id": self.id,
            "interest": self.interest,
            "interest-type": self.interestType,
            "amount": self.amount,
            "loaner-id": "BANK" if not self.loaner else self.loaner.id,
            "loanee-id": self.loanee.id,
            "amount-per-turn": self.amountPerTurn,
            "remaining-to-pay": self.totalOwed,
            "deadline": self.deadline
        }



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
    bankrupt: bool
    inDebtTo: "Player"
    
    inJail: bool
    jailDoublesRemaining: int

    loans: list[Loan]

    gameid: float

    JAIL_FAIL = 0
    JAIL_ESCAPE = 1
    JAIL_FORCE_LEAVE = -1

    def __init__(self, id: str, playerNumber: int, client, money: int = 1500):
        self.money = money
        self.id = id
        self.playerNumber = playerNumber
        self.ownedSpaces = []
        self.name = "Timmy 3 (You were the third Timmy!)"
        #this is PIECE
        self.piece = "PIECE"
        self.client = client
        self.bankrupt = False
        self.sets = []
        self.lastRoll = 0
        self.inJail = False
        self.jailDoublesRemaining = 3
        self.loans = []
        self.inDebtTo = None
        self.gameid = 0

    @property
    def propertyWorth(self):
        propertyWorth = 0
        for space in self.ownedSpaces:
            if not space.mortgaged:
                propertyWorth += space.cost / 2
            
                if space.houses != 0:
                    propertyWorth += (space.house_cost * space.houses / 2)
                
                if space.hotel:
                    propertyWorth += space.hotel_cost / 2
                
        
        return propertyWorth

    def takeOwnership(self, space: "Space", cost = 0):
        self.money -= cost
        self.ownedSpaces.append(space)
        space.owner = self

    def loanPlayer(self, other: Self, loan: Loan):
        other.loans.append(loan)
        self.money -= loan.amount
        other.money += loan.amount

    def payTurnLoans(self):
        for loan in self.loans:
            if loan.type == 'per-turn':
                loan.payTurnAmount()
                #FIXME: lets say the player has 3 loans, if the player goes bankrupt
                #while paying the first one, the other 2 will not get paid this turn.
                if self.money < 0:
                    self.bankrupt = True
                    yield BANKRUPT(self.id)
                    break

    def payLoan(self, loan: Loan, amount: int):
        loan.payAmount(amount)

    def trade(self, board: "Board", other: Self, trade: dict[str, Any]):
        for id in trade["give"].get("properties", []):
            space = board.getSpaceById(id)
            if not space or space in other.ownedSpaces:
                continue
            other.ownedSpaces.append(space)
            self.ownedSpaces.remove(space)
            space.owner = other

        if a := trade["give"].get("money"):
            other.gain(a)
            self.money -= a

        for id in trade["want"].get("properties", []):
            space = board.getSpaceById(id)
            if not space or space in self.ownedSpaces:
                continue
            other.ownedSpaces.remove(space)
            self.ownedSpaces.append(space)
            space.owner = self

        if a := trade["want"].get("money"):
            other.money -= a
            self.gain(a)

    def gotoJail(self, jail: "Space"):
        self.jailDoublesRemaining = 3
        self.inJail = True
        self.space = jail

    def leaveJail(self):
        self.inJail = False

    def payBail(self, jail: "Space"):
        if jail.owner:
            self.pay(jail.attrs["bailcost"], jail.owner)
        else:
            self.money -= jail.attrs["bailcost"]
        self.leaveJail()


    def tryLeaveJailWithDice(self, jailOwned: bool, roll1: int, roll2: int):
        """
        returns Player.JAIL_DOUBLES_SUCCESS if the double succeeds
        returns Player.JAIL_DOUBLES_FAIL if the double fails
        returns Player.JAIL_DOUBLES_FORCE_LEAVE if the player must leave jail
        """
        if jailOwned:
            if roll1 + roll2 >= 9:
                return Player.JAIL_ESCAPE
            else:
                return Player.JAIL_FAIL

        if roll1 == roll2:
            return Player.JAIL_ESCAPE
        self.jailDoublesRemaining -= 1
        if self.jailDoublesRemaining == 0:
            return Player.JAIL_FORCE_LEAVE
        return Player.JAIL_FAIL

    def owns(self, space: "Space"):
        return False if not space.owner else space.owner.id == self.id
    
    def gain(self, amount):
        
        if self.inDebtTo != None:
            if self.money + amount > 0:
                self.inDebtTo.money += (amount - abs(self.money))
            else:
                self.inDebtTo.money += amount
            if self.money >= 0:
                self.inDebtTo = None
                
        self.money += amount

    def pay(self, amount: int, other: Self):
        self.money -= amount
        other.money += amount

    def payRent(self, other: Self, space: "Space") -> statusreturn_t:
        amount = space.calculatePropertyRent(self.hasSet(space.color, space.set_size))
        self.pay(amount, other)
        if self.money < 0:
            self.inDebtTo = space.owner
        return PAY_OTHER(amount, self.id, other.id)
    
    def goBankrupt(self):
        self.bankrupt = True
        if self.inDebtTo != None:
            self.inDebtTo.money += self.propertyWorth
            
        for property in self.ownedSpaces:
            property.owner = None
        

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
            return BUY_FAIL(space.id)

        self.money -= space.cost
        space.owner = self
        self.ownedSpaces.append(space)

        if space.color not in self.sets and space.set_size and self.hasSet(space.color, space.set_size):
            self.sets.append(space.color)
            return BUY_NEW_SET(space.id)
        return BUY_SUCCESS(space.id)
        
    def mortgage(self, space: "Space"):
        if self is not space.owner or space.owner is None:
            return FAIL(self.id)
        self.gain(space.cost * 0.50)
        space.mortgaged = True
        return MORTGAGE_SUCCESS(self.id, space.id)
        
    def unmortgage(self, space: "Space"):
        if self is not space.owner or space.owner is None:
            return FAIL(self.id)
        self.money -= space.cost * 0.10
        space.mortgaged = False
        return UNMORTGAGE_SUCCESS(self.id, space.id)

    def buyHouse(self, space: "Space"):
        if not self.canBuyHouse(space):
            return BUY_HOUSE_FAIL(space.id)
        
        self.money -= space.house_cost
        space.houses += 1
        return BUY_HOUSE_SUCCESS(space.id)
    
    def buyHotel(self, space: "Space"):
        if not self.canBuyHotel(space):
            return BUY_HOTEL_FAIL(space.id)
        
        self.money -= space.house_cost
        space.hotel = True
        return BUY_HOTEL_SUCCESS(space.id)
        
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
    
    def sellHouse(self, space: "Space"):
        canSellHouse = True
        set_spaces = [s for s in self.ownedSpaces if s.color == space.color]
        for player_space in set_spaces:
            if space.houses < player_space.houses or (space.hotel and not player_space.hotel):
                canSellHouse = False
                
        if not canSellHouse:
            return False
        
        if space.hotel:
            space.hotel = False
            self.gain(space.hotel_cost / 2)
        else:
            space.houses -= 1
            self.gain(space.house_cost / 2)
            
        
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

    def incrementTurnsPassedOnLoans(self):
        for loan in self.loans:
            loan.turnsPassed += 1
            if loan.turnsPassed > loan.deadline:
                yield loan

    def toJson(self):
        return {
            "money": self.money,
            "id": self.id,
            "playerNumber": self.playerNumber,
            "piece": self.piece,
            "space": self.space.id,
            "sets": self.sets,
            "name": self.name,
            "ownedSpaces": [space.toJsonForPlayer() for space in self.ownedSpaces],
            "bankrupt": self.bankrupt,
            "injail": self.inJail,
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
    mortgaged: bool

    gameId: float

    def __init__(self, gameid: float, spaceType: spacetype_t, cost: int, name: str, purchaseable: bool, **kwargs):
        self.spaceType = spaceType
        self.players = []
        self.cost = cost
        self.name = name
        self.next = None
        self.prev = None
        self.attrs = kwargs
        self.owner = None
        self.id = random.randint(1,10000)

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
        space = Space(self.gameId, self.spaceType, cost=self.cost, name=self.name, purchaseable=self.purchaseable, **self.attrs)
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
    playerSpaces: dict[player_t, Space]
    players: dict[player_t, Player]
    spaces: dict[int, Space]

    eventHandlers: dict[str, ModuleType]
    boardName: str

    chanceCards: list[Chance]

    gameId: float

    def __init__(self, gameid: float, name: str, eventHandlers: dict[str, ModuleType], startSpace: Space, chanceCards: list[Chance]):
        self.startSpace = startSpace

        self.playerSpaces = {}
        self.players = {}

        self.gameId = gameid
        
        self.spaces = {space.id: space for space in startSpace.iterSpaces()}

        self.eventHandlers = eventHandlers
        self.boardName = name

        self.chanceCards = chanceCards

    def drawChance(self, player: Player):
        if self.chanceCards:
            return random.choice(self.chanceCards)
        return Chance("None", "gain", 0)

    def executeChanceCard(self, player: Player, card: Chance):
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
                    space = random.choice(list(self.spaces.values()))
                else:
                    n = 1
                if not pickedSpace:
                    space = self.getSpaceByName(spaceName, n)
                yield from self.moveTo(player, space)
            case "teleport-next-type":
                ty = str2spacetype(card.data)
                for space in player.space.next.iterSpaces():
                    if space.spaceType == ty:
                        yield from self.moveTo(player, space)
                        break

    def isValidSpaceName(self, name: str):
        for space in self.startSpace.iterSpaces():
            if space.name.lower() == name.lower():
                return True

    def addPlayer(self, player: Player):
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
        for dueLoan in player.incrementTurnsPassedOnLoans():
            yield DUE_LOAN(dueLoan.id, player.id)

        yield from self.runevent("onroll", player.space, player, amount, d1, d2)

    #call order  using an example event: onland
    #space.onland (DOES NOT STOP HERE)
    #<board-name>.onland_<space-name>()
    #<generic>.onland_<spae-name>()
    #<board-name>.onland()
    #<generic>.onland()
    def runevent(self, name: str, space: Space, player: Player, *args: Any):
        if hasattr(space, name):
            yield from getattr(space, name)(player, *args)

        for fn in (f"{name}_{space.name.replace(" ", "_").lower()}", name):
            if hasattr(self.eventHandlers.get(self.boardName), fn):
                yield from getattr(self.eventHandlers[self.boardName], fn)(self, space, player, *args)
                return
            elif hasattr(self.eventHandlers["generic"], fn):
                yield from getattr(self.eventHandlers["generic"], fn)(self, space, player, *args)
                return


    #moves the player DOES NOT ROLL DICE
    def move(self, player: Player, amount: int) -> Generator[statusreturn_t]:
        curSpace = self.playerSpaces[player.id]

        yield from self.runevent("onleave", curSpace, player)
        for i in range(amount):
            if amount > 0:
                curSpace = curSpace.next
            else:
                curSpace = curSpace.prev
            yield from self.runevent("onpass", curSpace, player)

        self.playerSpaces[player.id] = curSpace

        yield from self.runevent("onland", curSpace, player)

    def toJson(self):
        dict =  {
        "spaces": [ space.toJson() for space in self.startSpace.iterSpaces()],
        "playerSpaces": {k: v.toJson() for k, v in self.playerSpaces.items()}
        }    
        return dict
