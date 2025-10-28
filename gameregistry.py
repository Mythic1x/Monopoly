from typing import Any

type gameid_t = float

registry: dict[gameid_t, Any] = {}

def addgame(id: gameid_t, game: Any):
    registry[id] = game

def getgame(id: gameid_t):
    return registry.get(id)
