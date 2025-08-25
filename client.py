import abc
import json
from typing import Any, override

from board import Player, Space
from dataclasses import dataclass
    
class Client(abc.ABC):
    @abc.abstractmethod
    async def read(self, prompt: str) -> str: ...

    @abc.abstractmethod
    async def write(self, data: dict): ...

    @abc.abstractmethod
    async def __anext__(self) -> dict[str, Any]: ...

    async def handleStatus(self, status: str, player: Player, data: list[Any]):
        status = await getattr(self, status)(player, *data)
        return status

    async def PROMPT_TO_BUY(self, player: Player, space: Space):
        await self.write({"response": "notification", "value": f"{space.name} is available for purchase for the price of ${space.cost}"})

    async def MONEY_LOST(self, player: Player, amount: int):
        await self.write({"response": "notification", "value": f"{player.name} lost {amount}"})

    async def BUY_SUCCESS(self, player: Player, space: Space):
        await self.write({"response": "notification", "value": f"{player.name} successfully bought {space.name}"})

    async def BUY_FAIL(self, player: Player, space: Space):
        await self.write({"response": "notification", "value": f"{player.name} failed"})

    async def BUY_NEW_SET(self, player: Player, space: Space):
        await self.write({"response": "notification", "value": f"{player.name} successfully bought {space.name} for a complete {space.color} set"})
    async def MONEY_GIVEN(self, player: Player, amount: int):
        await self.write({"response": "notification", "value": f"{player.name} gained {amount}"})

    async def NONE(self, *data):
        pass

    def __aiter__(self):
        return self

class WSClient(Client):
    def __init__(self, ws):
        self.ws = ws

    @override
    async def read(self, prompt: str) -> str:
        await self.ws.send(json.dumps({"response": "prompt", "value": prompt}))
        return await self.ws.recv()

    @override
    async def write(self, data: dict):
        await self.ws.send(json.dumps(data))
    
    @override
    async def __anext__(self) -> dict[str, Any]:
        return json.loads(await self.ws.recv())

class TermClient(Client):

    @override
    async def handleStatus(self, status: str, player: Player, data: list[Any]):
        val = await super().handleStatus(status, player, data)
        return val

    @override
    async def read(self, prompt: str) -> str:
        return input(prompt)

    @override
    async def write(self, data: dict):
        print(data)

    @override
    async def __anext__(self) -> dict[str, Any]:
        res = input("> ")
        if res == "end-turn":
            return {"action": "end-turn"}
        return {"action": "start-turn"}
