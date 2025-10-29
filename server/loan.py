from typing import TYPE_CHECKING
import random

from monopolytypes import *
from gameregistry import *

if TYPE_CHECKING:
    from player import Player


class Loan:
    id: float
    type: str  # deadline | per-turn
    amountPerTurn: int
    deadline: int
    amount: int
    interest: int
    interestType: str  # simple | compound
    status: str  # declined | accepted | proposed
    turnsPassed: int
    gameid: gameid_t

    totalOwed: int
    loaner: "Player | None"
    loanee: "Player"

    def __init__(
        self,
        gameid: gameid_t,
        loaner: player_t | None,
        loanee: player_t,
        type: str,
        amount: int,
        interest: int,
        interestType: str,
        status: str,
        amountPerTurn: int = 0,
        deadline: int = 0,
    ) -> None:
        self.id = random.random()
        self.gameid = gameid
        self.type = type
        self.amount = amount
        self.interest = interest
        self.interestType = interestType
        self.status = status

        self.amountPerTurn = amountPerTurn
        self.deadline = deadline

        self.turnsPassed = 0

        game = getgame(self.gameid)

        assert game, f"game (id = {self.gameid}) is undefined"

        self.loaner = game.getplayer(loaner) if loaner != "Bank" else None
        self.loanee = game.getplayer(loanee)

        self.totalOwed = amount
        if self.type == "simple":
            self.totalOwed = round(self.totalOwed * (1 + (interest / 100)))

    def compound(self):
        if self.interestType == "simple":
            return
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
            "interestType": self.interestType,
            "amount": self.amount,
            "loaner": "BANK" if not self.loaner else self.loaner.id,
            "loanee": self.loanee.id,
            "amountPerTurn": self.amountPerTurn,
            "remainingToPay": self.totalOwed,
            "deadline": self.deadline,
            "status": self.status,
            "turnsPassed": self.turnsPassed,
        }
