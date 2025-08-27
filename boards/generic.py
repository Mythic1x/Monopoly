from board import MONEY_GIVEN, NONE, PASS_GO, PAY_OTHER, PAY_TAX, PROMPT_TO_BUY, ST_RAILROAD, ST_UTILITY, Board, Space, Player

def onrent(board: Board, space: Space, player: Player):
    pass

def onpass_passing_go(board: Board, space: Space, player: Player):
    player.money += abs(space.cost)
    yield PASS_GO(abs(space.cost))

def onrent_utility(board: Board, space: Space, player: Player):
    if space.owner is None or space.owner.id == player.id:
        return NONE()
    amount = len(player.getUtilities()) * player.lastRoll
    player.pay(amount, space.owner)
    return PAY_OTHER(amount, player, space.owner)

def onrent_railroad(board: Board, space: Space, player: Player):
    if space.owner is None :
        return NONE()
    owed = {
            0: 0,
            1: 25,
            2: 50,
            3: 100,
            4: 100
    }[space.owner.getOwnedRailroads()]
    if owed:
        player.pay(owed, space.owner)
        return PAY_OTHER(owed, player, space.owner)

def onland_income_tax(board: Board, space: Space, player: Player):
    player.money -= round(player.money * 0.10)
    yield PAY_TAX(round(player.money * 0.10), "income")

def onland_luxurytax(board: Board, space: Space, player: Player):
    player.money -= 75
    yield PAY_TAX(75, "luxury")

def onland_go_to_jail(board: Board, space: Space, player: Player):
    jail = board.findJail()
    if jail:
        player.gotoJail(jail)
        yield from board.moveTo(player, jail)

def onland(board: Board, space: Space, player: Player):
    print(f"You landed on {space.name}")

    if space.cost < 0:
        player.money += abs(space.cost)
        yield MONEY_GIVEN(abs(space.cost))
        return

    print(space.purchaseable)
    if space.isUnowned() and space.purchaseable:
        yield PROMPT_TO_BUY(space)

    if not player.owns(space) and space.owner:
        if space.spaceType == ST_UTILITY:
            onrent_utility(board, space, player)
            yield NONE()
            return
        elif space.spaceType == ST_RAILROAD:
            onrent_railroad(board, space, player)
            yield NONE()
            return

        rent = space.attrs.get("rent")
        if not rent:
            yield NONE()
            return
        if rent:
            yield player.payRent(space.owner, space)
            return

    yield NONE()
