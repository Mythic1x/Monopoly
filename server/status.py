from dataclasses import dataclass
from typing import Any
from monopolytypes import *

class status_t:
    level: int = 3
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
    level: int = 1


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
    auction_dict: dict[Any, Any]
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
