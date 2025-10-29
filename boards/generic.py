import random
from board import DRAW_CHANCE, NONE, PASS_GO, PAY_JAIL, PAY_OTHER, PAY_TAX, PROMPT_TO_BUY, ST_RAILROAD, ST_UTILITY, Board, Space
from player import Player

def onroll(board: Board, space: Space, player: Player, amount: int, d1: int, d2: int):
    yield from board.move(player, amount)

def onroll_jail(board: Board, space: Space, player: Player, amount: int, d1: int, d2: int):
    if not player.inJail:
        yield from onroll(board, space, player, amount, d1, d2)
        return

    match player.tryLeaveJailWithDice(True if space.owner else False, d1, d2):
        case Player.JAIL_FAIL:
            return
        case Player.JAIL_ESCAPE:
            player.leaveJail()
            yield NONE()
        case Player.JAIL_FORCE_LEAVE:
            yield from board.runevent("onbail", player.space, player)

def onbail(board: Board, space: Space, player: Player):
    bail = space.attrs["bailcost"]
    if space.owner:
        player.pay(bail, space.owner)
    else:
        player.money -= bail

    player.leaveJail()

    yield PAY_JAIL(bail)

def onrent(board: Board, space: Space, player: Player):
    pass

def onpass_passing_go(board: Board, space: Space, player: Player):
    player.money += space.cost
    yield PASS_GO(space.cost)

def onrent_utility(board: Board, space: Space, player: Player):
    if space.owner is None or space.owner.id == player.id:
        return NONE()
    amount = len(player.getUtilities()) * player.lastRoll
    player.pay(amount, space.owner)
    return PAY_OTHER(amount, player.id, space.owner.id)

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
        return PAY_OTHER(owed, player.id, space.owner.id)

def onland_chance(board: Board, space: Space, player: Player):
    card = board.drawChance(player)
    yield from board.executeChanceCard(player, card)
    yield DRAW_CHANCE(card.event, player.id)

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

    if space.isUnowned() and space.purchaseable:
        yield PROMPT_TO_BUY(space.id)

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
