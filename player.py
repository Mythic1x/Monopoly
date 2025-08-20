class Player:
    money: int
    id: str

    def __init__(self, id: str, money: int = 100):
        self.money = money
        self.id = id

    def go(self):
        pass
