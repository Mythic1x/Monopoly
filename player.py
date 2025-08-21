from board import Board, Space, spacetype_t
import random
class Player:
    money: int
    id: str
    playerNumber: int
    dSides: int
    ownedSpaces: list[Space]

    def __init__(self, id: str, dSides: int, playerNumber: int, money: int = 100):
        self.money = money
        self.id = id
        self.dSides = dSides
        self.playerNumber = playerNumber
        self.ownedSpaces = []

    def go(self, board: Board):
        if board.playerTurn is not self.playerNumber:
            print("not your turn")
            return
        amount = random.randint(1, self.dSides)
        board.move(self, amount)
        
    def getOwnedRailroads(self):
        number = 0
        for space in self.ownedSpaces:
            if space.spaceType is spacetype_t.ST_RAILROAD:
                number += 1
        return number
