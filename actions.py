import asyncio
import json
from board import Player

def getUpdatedState(game):
    return [
        {"response": "next-turn", "value": game.curPlayer.toJson()},
        {"response": "board", "value": game.board.toJson()},
        {"response": "player-list", "value": [player.toJson() for player in game.players.values()]}
    ]

def endTurn(game, action, player: Player):
    if game.activeAuction: return
    if game.curPlayer.bankrupt:
        yield False, {
                "response": "notification", "value": "turn cannot be end while bankrupt"
        }
        return
    prevPlayer = game.curPlayer
    game.advanceTurn()
    yield True, [
        {"response": "turn-ended", "value": prevPlayer.toJson()},
        {"response": "next-turn", "value": game.curPlayer.toJson()}
    ]

def sendPlayerInfo(game, action, player: Player):
    yield False, {"response": "player-info", "value": player.toJson()}

def payBail(game, action, player: Player):
    if not player.inJail: return

    player.payBail(player.space)
    yield True, {"response": "notification", "value": f"{player.name} paid bail"}
    yield True, getUpdatedState(game)

def setBail(game, action, player: Player):
    spaceid = action["spaceid"]
    amount = action["amount"]
    space = game.board.getSpaceById(spaceid)
    if not space:
        yield False, {"response": "error", "value": f"space id {spaceid} does not exist"}
    elif not isinstance(amount, int):
        yield False, {"response": "error", "value": f"{amount} is not an integer"}
    else:
        space.attrs["bailcost"] = amount
        yield True, getUpdatedState(game)

def connect(game, action, player: Player):
    yield False, {"response": "assignment", "value": player.id}
    yield True, [
        {"response": "board", "value": game.board.toJson()},
        {"response": "next-turn", "value": game.curPlayer.toJson()}
    ]
    yield False, {"response": "current-space", "value": player.space.toJson()}
    yield True, {"response": "player-list", "value": [player.toJson() for player in game.players.values()]}
    if game.activeAuction is not None: 
        yield True, ({"response": "auction-status", "value": game.activeAuction})

def teleport(game, action, player: Player):
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

def roll(game, action, player: Player):
    if game.activeAuction: return
    for status in game.board.rollPlayer(player, game.dSides):
        yield status.broadcast, status
    yield False, {"response": "roll-complete", "value": None}
    yield True, getUpdatedState(game)

def setDetails(game, action, player: Player):
    details = action["details"]
    player.name = details["name"]
    player.piece = details["piece"]

def requestSpace(game, action, player: Player):
    yield False, {"response": "current-space", "value": player.space.toJson()}

def bankrupt(game, action, player: Player):
    yield True, {"response": "bankrupt", "value": f"{player.name}"}
    player.goBankrupt()
    
    game.activePlayers.remove(player)
    yield False, {"response": "player-info", "value": player.toJson()}

    if len(game.activePlayers) < 2:
        yield True, {"response": "game-end", "value": game.activePlayers[0].toJson()}

    if game.curTurn >= len(game.activePlayers):
        game.curTurn = 0

    yield True, getUpdatedState(game)

def setMoney(game, action, player: Player):
    player.money = int(action["money"])

def buy(game, action, player: Player):
    property = game.board.spaces[action["spaceid"]]
    result = player.buy(property)
    yield True, result
    yield True, getUpdatedState(game)

def startAuction(game, action, player: Player):
    space = game.board.spaces[action["spaceid"]]

    game.createAuction(space.id, end_time=10000)

    yield True, {"response": "auction-status", "value": game.activeAuction}
    asyncio.create_task(game.auctionTimer())                

def bid(game, action, player: Player):
    bid = int(action['bid'])
    if not game.activeAuction or player.money < game.activeAuction['current_bid'] or bid < game.activeAuction["current_bid"]:
        yield False, {"response": "notification", "value": "you can't do that stop cheating"}
    if game.activeAuction:
        game.updateAuction(bidder=player.id, current_bid=bid)
        yield True, {"response": "auction-status", "value": game.activeAuction}

def buyHouse(game, action, player: Player):
    property = game.board.spaces[action["spaceid"]]
    result = player.buyHouse(property)
    yield True, result
    yield True, getUpdatedState(game)

def buyHotel(game, action, player: Player):
    property = game.board.spaces[action["spaceid"]]
    result = player.buyHotel(property)
    yield True, result
    yield True, getUpdatedState(game)
    
def sellHouse(game, action, player: Player):
    property = game.board.spaces[action["spaceid"]]
    result = player.sellHouse(property)
    yield True, result
    yield True, getUpdatedState(game)

#trade obj should look like
#{"want": {"properties": ["id 1", "id2", "id3"], "money": 432483}, "give": {"money": 3432}}
def proposeTrade(game, action, player: Player):
    trade = action["trade"]
    to = action["playerid"]
    fromPlayer = action["from"]
    p = game.players.get(to)
    if not p:
        yield False, {"response": "notification", "value": "invalid player id"}
    else:
        yield p.client, ({"response": "trade-proposal", "value": {"trade": trade, "with": player.id, "from": fromPlayer}})

def acceptTrade(game, action, player: Player):
    trade = action["trade"]
    tradeWith = action["from"]
    otherPlayer = game.players.get(tradeWith)
    if otherPlayer:
        #we do otherPlayer.trade(player) because otherPlayer is the player who initialized the trade in the first place
        otherPlayer.trade(game.board, player, trade)
    yield True, getUpdatedState(game)
    
def mortgage(game, action, player: Player):
    space = game.board.getSpaceById(action["spaceid"])
    yield True, player.mortgage(space)
    yield True, getUpdatedState(game)
    
def unmortgage(game, action, player: Player):
    space = game.board.getSpaceById(action["spaceid"])
    yield True, player.unmortgage(space)
    yield True, getUpdatedState(game)


