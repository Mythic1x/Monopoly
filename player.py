from board import Board, Space, ST_RAILROAD
import random
class Player:
    money: int
    id: str
    playerNumber: int
    ownedSpaces: list[Space]

    def __init__(self, id: str, playerNumber: int, money: int = 100):
        self.money = money
        self.id = id
        self.playerNumber = playerNumber
        self.ownedSpaces = []
        
    def getOwnedRailroads(self):
        number = 0
        for space in self.ownedSpaces:
            if space.spaceType is ST_RAILROAD:
                number += 1
        return number
