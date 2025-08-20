from player import Player
from util import LLNode, LinkedList

type spacetype_t = int

ST_PROPERTY: spacetype_t = 0
ST_COMMUNITY_CHEST: spacetype_t = 1
ST_CHANCE: spacetype_t = 2
ST_JAIL: spacetype_t = 3
ST_FREE_PARKING: spacetype_t = 4
ST_GOTO_JAIL: spacetype_t = 5
ST_GO: spacetype_t = 6
ST_LUXURY_TAX: spacetype_t = 7
ST_INCOME_TAX: spacetype_t = 8
ST_RAILROAD: spacetype_t = 9

class Space:
    spaceType: spacetype_t
    def __init__(self, spaceType: spacetype_t, *, cost: int, name: str):
        self.spaceType = spaceType

    def onland(self, player: Player):
        {
            ST_RAILROAD: onland_railroad,
        }[self.spaceType](self, player)

def onland_railroad(rr: Space, player: Player):
    pass

class Board:
    state: LinkedList[Space]
    def __init__(self, *spaces: Space):
        self.state = LinkedList[Space]()
        for space in spaces:
            self.state.append(space)

