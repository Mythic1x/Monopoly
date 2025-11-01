from typing import TYPE_CHECKING
import asyncio
from status import BANKRUPT
from trade import Trade

from loan import Loan

if TYPE_CHECKING:
    from game import Game
    from player import Player

def getUpdatedState(game: "Game"):
    return [
        {"response": "next-turn", "value": game.curPlayer.toJson()},
        {"response": "board", "value": game.board.toJson()},
        {
            "response": "player-list",
            "value": [player.toJson() for player in game.players.values()],
        },
        {"response": "trade-list", "value": [trade.toJson() for trade in game.trades]},
        {"response": "loan-list", "value": [loan.toJson() for loan in game.loans]},
        {"response": "lobby-state", "value": game.toJson()}
    ]


def endTurn(game: "Game", action, player: "Player"):
    if game.activeAuction:
        return
    if game.curPlayer.bankrupt:
        yield False, {
            "response": "notification",
            "value": "turn cannot be end while bankrupt",
        }
        return
    prevPlayer = game.curPlayer
    
    game.advanceTurn()
    yield True, [
        {"response": "turn-ended", "value": prevPlayer.toJson()},
        {"response": "next-turn", "value": game.curPlayer.toJson()},
    ]


def sendPlayerInfo(game: "Game", action, player: "Player"):
    yield False, {"response": "player-info", "value": player.toJson()}


def payBail(game: "Game", action, player: "Player"):
    if not player.inJail:
        return

    assert player.space, f"{player} is not on a space"
    player.payBail(player.space)
    yield True, {"response": "notification", "value": f"{player.name} paid bail"}
    yield True, getUpdatedState(game)


def setBail(game: "Game", action, player: "Player"):
    spaceid = action["spaceid"]
    amount = action["amount"]
    space = game.board.getSpaceById(spaceid)
    if not space:
        yield False, {
            "response": "error",
            "value": f"space id {spaceid} does not exist",
        }
    elif not isinstance(amount, int):
        yield False, {"response": "error", "value": f"{amount} is not an integer"}
    else:
        space.attrs["bailcost"] = amount
        yield True, getUpdatedState(game)


def connect(game: "Game", action, player: "Player"):
    assert player.space, f"{player} is not on a space"
    yield False, {"response": "assignment", "value": player.id}
    yield True, [
        {"response": "board", "value": game.board.toJson()},
        {"response": "next-turn", "value": game.curPlayer.toJson()},
    ]
    yield False, {"response": "current-space", "value": player.space.toJson()}
    yield True, {
        "response": "player-list",
        "value": [player.toJson() for player in game.players.values()],
    }
    if game.activeAuction is not None:
        yield True, ({"response": "auction-status", "value": game.activeAuction})
        
def startGame(game: "Game", action, player: "Player"):

    if len(game.activePlayers) > 1:
        game.started = True
        player.host = True
        yield True, ({"response": "lobby-state", "value": game.toJson()})
  


def teleport(game, action, player: "Player"):
    spaceId = action["spaceid"]
    playerId = action["playerid"]

    space = game.board.getSpaceById(spaceId)
    if not space:
        yield False, player.client.mknotif(f"invalid space id: {spaceId}")
    else:
        for status in game.board.moveTo(game.players[playerId], space):
            yield status.broadcast, status
        yield True, {"response": "board", "value": game.board.toJson()}
        yield True, getUpdatedState(game)


def roll(game: "Game", action, player: "Player"):
    if game.activeAuction:
        return
    for status in game.board.rollPlayer(player, game.dSides):
        yield status.broadcast, status
    yield False, {"response": "roll-complete", "value": None}
    yield True, getUpdatedState(game)


def setDetails(game: "Game", action, player: "Player"):
    details = action["details"]
    player.name = details["name"]
    player.piece = details["piece"]


def requestSpace(game: "Game", action, player: "Player"):
    assert player.space, f"{player} is not on a space"
    yield False, {"response": "current-space", "value": player.space.toJson()}


def bankrupt(game: "Game", action, player: "Player"):
    yield True, BANKRUPT(player.id)
    player.goBankrupt()

    game.activePlayers.remove(player)
    yield False, {"response": "player-info", "value": player.toJson()}

    if len(game.activePlayers) < 2:
        yield True, {"response": "game-end", "value": game.activePlayers[0].toJson()}

    if game.curTurn >= len(game.activePlayers):
        game.curTurn = 0

    yield True, getUpdatedState(game)


def setMoney(game: "Game", action, player: "Player"):
    player.money = int(action["money"])


def buy(game: "Game", action, player: "Player"):
    if game.curPlayer.id != player.id:
        yield False, { "response": "notification", "value": "Cannot buy when it's not your turn" }
        return

    property = game.board.spaces[action["spaceid"]]
    result = player.buy(property)
    yield True, result
    yield True, getUpdatedState(game)


def startAuction(game: "Game", action, player: "Player"):
    space = game.board.spaces[action["spaceid"]]

    game.createAuction(space.id, end_time=10000)

    yield True, {"response": "auction-status", "value": game.activeAuction}
    asyncio.create_task(game.auctionTimer())


def bid(game: "Game", action, player: "Player"):
    bid = int(action["bid"])
    if (
        not game.activeAuction
        or player.money < game.activeAuction["current_bid"]
        or bid < game.activeAuction["current_bid"]
    ):
        yield False, {
            "response": "notification",
            "value": "you can't do that stop cheating",
        }
    if game.activeAuction:
        game.updateAuction(bidder=player.id, current_bid=bid)
        yield True, {"response": "auction-status", "value": game.activeAuction}


def buyHouse(game: "Game", action, player: "Player"):
    property = game.board.spaces[action["spaceid"]]
    result = player.buyHouse(property)
    yield True, result
    yield True, getUpdatedState(game)


def buyHotel(game: "Game", action, player: "Player"):
    property = game.board.spaces[action["spaceid"]]
    result = player.buyHotel(property)
    yield True, result
    yield True, getUpdatedState(game)


def sellHouse(game: "Game", action, player: "Player"):
    property = game.board.spaces[action["spaceid"]]
    result = player.sellHouse(property)
    yield True, result
    yield True, getUpdatedState(game)


# trade obj should look like
# {"want": {"properties": ["id 1", "id2", "id3"], "money": 432483}, "give": {"money": 3432}}
def proposeTrade(game: "Game", action, player: "Player"):
    trade = Trade(action["trade"], player.id, action["playerid"], "proposed")
    p = game.players.get(trade.recipient)
    game.trades.append(trade)
    if not p:
        yield False, {"response": "notification", "value": "invalid player id"}
    else:
        yield p.client, (
            {
                "response": "trade-proposal",
                "value": trade.toJson(),
            }
        )
        yield True, getUpdatedState(game)


def acceptTrade(game: "Game", action, player: "Player"):
    trade = next(trade for trade in game.trades if trade.id == action["id"])
    trade.status = "accepted"
    otherPlayer = game.players.get(trade.sender)
    if otherPlayer:
        # we do otherPlayer.trade(player) because otherPlayer is the player who initialized the trade in the first place
        otherPlayer.trade(game.board, player, trade)
    yield True, getUpdatedState(game)


def declineTrade(game: "Game", action, player: "Player"):
    trade = next(trade for trade in game.trades if trade.id == action["id"])
    trade.status = "declined"
    yield True, getUpdatedState(game)
   


def mortgage(game: "Game", action, player: "Player"):
    space = game.board.getSpaceById(action["spaceid"])
    assert space, f"Space@:{action["spaceid"]} does not exist"
    yield True, player.mortgage(space)
    yield True, getUpdatedState(game)


def unmortgage(game: "Game", action, player: "Player"):
    space = game.board.getSpaceById(action["spaceid"])
    assert space, f"Space@:{action["spaceid"]} does not exist"
    yield True, player.unmortgage(space)
    yield True, getUpdatedState(game)


def loan(game: "Game", action, player: "Player"):
    loaner = action["loan"]["loaner"]
    loan = action["loan"]
    if loaner is None: #bank loan
        max_amount = player.creditScore * 2.5
        if loan["amount"] > max_amount:
            yield False, {"response": "notification", "value": "Your credit score is not high enough for this loan"}
        if loan["type"] == "deadline":
            if player.creditScore >= 800 and player.creditScore <= 500:
                deadline = 5
            else:
                deadline = 3
        else:
            yield False, {"response": "notification", "value": "Failed to get bank loan with per-turn payback"}
            return
        loan = Loan(
            player.gameid,
            "Bank",
            player.id,
            loan["type"],
            loan["amount"],
            loan["interest"],
            loan["interestType"],
            "accepted",
            loan["amountPerTurn"],
            deadline,
        )
        game.loans.append(loan)
        player.loans.append(loan)
        player.money += loan.amount
        yield True, {"response": "accepted-loan", "value": loan.toJson()}
        yield True, getUpdatedState(game)
        return

    loanee = game.players.get(action["loan"]["loaner"])
    assert loanee, f"Player@:{action["loan"]["loaner"]} does not exist"
    loan = Loan(
        player.gameid,
        loaner,
        player.id,
        loan["type"],
        loan["amount"],
        loan["interest"],
        loan["interestType"],
        loan["status"],
        loan["amountPerTurn"],
        loan["deadline"],
    )
    action["loan"]["id"] = loan.id
    game.loans.append(loan)
    
    yield loanee.client, ({"response": "loan-proposal", "value": loan.toJson()})
    yield True, getUpdatedState(game)


def acceptLoan(game: "Game", action, player: "Player"):
    loanId = action["loan"]
    loan: Loan = next(loan for loan in game.loans if loan.id == loanId)
    loan.status = "accepted"
    if loan.loaner:
        loaner = game.players.get(loan.loaner.id)
        assert loaner, f"Player@:{action["loan"]["loaner"]} does not exist"
        loaner.loanPlayer(loan.loanee, loan)
    yield True, {"response": "accepted-loan", "value": loan.toJson()}
    yield True, getUpdatedState(game)


def declineLoan(game: "Game", action, player: "Player"):
    loanId = action["loan"]
    loan = next(loan for loan in game.loans if loan.id == loanId)
    loan.status = "declined"
    yield True, getUpdatedState(game)
    
def payLoan(game: "Game", action, player: "Player"):
    loanId = action["loan"]
    amount = action["amount"]
    loan: Loan = next(loan for loan in game.loans if loan.id == loanId)
    player.payLoan(loan, amount)
    if loan.totalOwed <= 0:
        player.loans.remove(loan)
        player.increaseCreditScore(loan.amount)
