import random
from typing import Any

from monopolytypes import player_t

class Trade:
    trade: Any
    sender: player_t
    recipient: player_t
    id: float
    status: str #declined | accepted | proposed

    def __init__(self, trade: "Trade", sender: player_t, recipient: player_t, status: str):
        self.trade = trade
        self.sender = sender
        self.recipient = recipient
        self.status = status
        self.id = random.random()

    def toJson(self):
        return {
            "id": self.id,
            "trade": self.trade,
            "sender": self.sender,
            "recipient": self.recipient,
            "status": self.status,
        }
