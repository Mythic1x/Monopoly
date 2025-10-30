from typing import TYPE_CHECKING, override, Self

import math
import random

from status import PAY_OTHER

from board import *

if TYPE_CHECKING:
    from client import Client
    from trade import Trade
    from loan import Loan

class Player:
    client: "Client"
    money: int
    id: str
    playerNumber: int
    ownedSpaces: list["Space"]
    # a list of sets by color
    sets: list[str]
    name: str
    space: "Space | None"
    piece: str
    lastRoll: int
    bankrupt: bool
    inDebtTo: "Player | None"
    creditScore: int
    color: str

    inJail: bool
    jailDoublesRemaining: int

    loans: list["Loan"]

    gameid: float

    JAIL_FAIL: int = 0
    JAIL_ESCAPE: int = 1
    JAIL_FORCE_LEAVE: int = -1

    def __init__(self, id: str, playerNumber: int, client: "Client", money: int = 1500):
        self.money = money
        self.id = id
        self.playerNumber = playerNumber
        self.ownedSpaces = []
        self.name = "Timmy 3 (You were the third Timmy!)"
        # this is PIECE
        self.piece = "PIECE"
        self.client = client
        self.space = None
        self.bankrupt = False
        self.sets = []
        self.lastRoll = 0
        self.inJail = False
        self.jailDoublesRemaining = 3
        self.loans = []
        self.inDebtTo = None
        self.gameid = 0
        self.color = f"#{random.randint(180, 255):x}{random.randint(180, 255):x}{random.randint(180, 255):x}"
        self.creditScore = 300

    @override
    def __str__(self):
        return f"Player@{self.name}:{self.id}"

    @property
    def propertyWorth(self):
        propertyWorth = 0
        for space in self.ownedSpaces:
            if not space.mortgaged:
                propertyWorth += space.cost // 2

                if space.houses != 0:
                    propertyWorth += int(space.house_cost * space.houses / 2)

                if space.hotel:
                    propertyWorth += int(space.hotel_cost / 2)

        return propertyWorth

    def takeOwnership(self, space: Space, cost: int = 0):
        assert (
            cost <= self.money
        ), f"Cannot buy {space.name} for ${cost} because {self} only has ${self.money}"
        self.money -= cost
        self.ownedSpaces.append(space)
        space.owner = self

    def loanPlayer(self, other: Self, loan: "Loan"):
        assert (
            self.money >= loan.amount
        ), f"Cannot loan {loan.amount} because {self} only has ${self.money}"
        other.loans.append(loan)
        self.money -= loan.amount
        other.money += loan.amount

    def payTurnLoans(self):
        for loan in self.loans:
            if loan.type == "per-turn":
                loan.payTurnAmount()
                # FIXME: lets say the player has 3 loans, if the player goes bankrupt
                # while paying the first one, the other 2 will not get paid this turn.
                if self.money < 0:
                    self.inDebtTo = loan.loaner
                    self.creditScore -= 100
                    break
                if loan.totalOwed <= 0:
                    self.loans.remove(loan)
                    self.increaseCreditScore(loan.amount)

    def payLoan(self, loan: "Loan", amount: int):
        loan.payAmount(amount)
        if self.money < 0:
            self.inDebtTo = loan.loaner

    def increaseCreditScore(self, amount: int):
        if self.creditScore >= 800:
            return
        amountToIncrease = amount / 4
        if self.creditScore + amountToIncrease > 800:
            self.creditScore = 800
        else:
            self.creditScore += math.floor(amountToIncrease)

    def trade(self, board: "Board", other: "Player", trade: "Trade"):
        for id in trade.give.get("properties", []):
            space = board.getSpaceById(id)
            if not space or space in other.ownedSpaces:
                continue
            other.ownedSpaces.append(space)
            self.ownedSpaces.remove(space)
            space.owner = other

        if a := trade.give.get("money"):
            other.gain(a)
            self.money -= a

        for id in trade.want.get("properties", []):
            space = board.getSpaceById(id)
            if not space or space in self.ownedSpaces:
                continue
            other.ownedSpaces.remove(space)
            self.ownedSpaces.append(space)
            space.owner = self

        if a := trade.want.get("money"):
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
        # if the jail is owned, rolling should work differently
        if jailOwned:
            # the person in jail only needs to roll >= 9 to make it easier to get out
            # also there are unlimited tries
            if roll1 + roll2 >= 9:
                return Player.JAIL_ESCAPE
            else:
                return Player.JAIL_FAIL

        # otherwise the player needs to roll doubles
        if roll1 == roll2:
            return Player.JAIL_ESCAPE

        self.jailDoublesRemaining -= 1
        # if they run out of tries, they are forced to leave and pay bail
        if self.jailDoublesRemaining == 0:
            return Player.JAIL_FORCE_LEAVE
        return Player.JAIL_FAIL

    def owns(self, space: "Space"):
        return False if not space.owner else space.owner.id == self.id

    def gain(self, amount: int):

        if self.inDebtTo != None:
            if self.money + amount > 0:
                self.inDebtTo.money += amount - abs(self.money)
            else:
                self.inDebtTo.money += amount
            if self.money >= 0:
                self.inDebtTo = None

        self.money += amount

    def pay(self, amount: int, other: "Player"):
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

        if (
            space.color not in self.sets
            and space.set_size
            and self.hasSet(space.color, space.set_size)
        ):
            self.sets.append(space.color)
            return BUY_NEW_SET(space.id)
        return BUY_SUCCESS(space.id)

    def mortgage(self, space: "Space"):
        if self is not space.owner or space.owner is None:
            return FAIL(self.id)
        self.gain(int(space.cost * 0.50))
        space.mortgaged = True
        return MORTGAGE_SUCCESS(self.id, space.id)

    def unmortgage(self, space: "Space"):
        if self is not space.owner or space.owner is None:
            return FAIL(self.id)
        self.money -= int(space.cost * 0.10)
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
            if space.houses < player_space.houses or (
                space.hotel and not player_space.hotel
            ):
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

    def incLoanDeadline(self):
        for loan in self.loans:
            if not loan.deadline:
                continue
            loan.turnsPassed += 1
            if loan.turnsPassed > loan.deadline:
                yield loan

    def compoundLoans(self):
        for loan in self.loans:
            if loan.interestType != "compound":
                continue
            loan.compound()

    def toJson(self):
        return {
            "money": self.money,
            "id": self.id,
            "playerNumber": self.playerNumber,
            "piece": self.piece,
            "space": self.space.id if self.space else None,
            "sets": self.sets,
            "name": self.name,
            "ownedSpaces": [space.toJsonForPlayer() for space in self.ownedSpaces],
            "bankrupt": self.bankrupt,
            "injail": self.inJail,
            "loans": [loan.toJson() for loan in self.loans],
            "color": self.color,
            "creditScore": self.creditScore,
        }
