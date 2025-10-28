import asyncio
import json
import sys

from typing import Any, Callable
from websockets.asyncio.server import ServerConnection, serve


from board import Player
from client import WSClient, TermClient
from game import Game
ipConnections: dict[Any, Player] = {}


class Lobby:
    players: list[Player]
    def __init__(self):
        self.players = []

    def join(self, p: Player):
        self.players.append(p)

    async def moveToGame(self, player: Player, game: Game, onjoin: Callable[[], Any] | None = None):
        if player not in self.players:
            return
        self.players.remove(player)
        response = json.loads(await player.client.read('waiting for details'))
        details = response['details']
        player.name = details['name']
        player.piece = details['piece']
        player.gameid = game.id
        await player.client.write({"response": "join-game", "value": "join"})
        await game.join(player, onjoin)



game = Game("main")
lobby = Lobby()

async def gameServer(ws: ServerConnection):
    c = WSClient(ws)

    if ws.remote_address[0] in ipConnections:
        player = ipConnections[ws.remote_address[0]]
        game.disconnectClient(player.client)
        player.client = c
        await player.client.write({"response": "reconnect", "value": {"name": player.name, "piece": player.piece}})
        await game.rejoin(player)
    else:
        player = Player(str(ws.id), len(game.clients), c)
        lobby.join(player)
        await lobby.moveToGame(player, game, onjoin=lambda: ipConnections.__setitem__(ws.remote_address[0], player))
        

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "t":
        c = TermClient()
        player = Player("1", len(game.clients), c)
        lobby.join(player)
        await lobby.moveToGame(player, game)
    else:
        async with serve(gameServer, "0.0.0.0", 8765) as server:
            await server.serve_forever()

asyncio.run(main())
