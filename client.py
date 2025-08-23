import abc
from typing import Any, override

from board import Player, Space
from dataclasses import dataclass
    
class Client(abc.ABC):
    @abc.abstractmethod
    async def read(self, prompt: str) -> str: ...

    @abc.abstractmethod
    async def write(self, data: str): ...

    @abc.abstractmethod
    async def __anext__(self) -> dict[str, Any]: ...
    
    

    async def handleStatus(self, player: Player, status: str, data: list[Any]):
        status = await getattr(self, status)(player, *data)
        return status

    async def PROMPT_TO_BUY(self, player: Player, space: Space):
        status = await self.read(f"would you like to buy: {space.name}")
        if status == "yes":
            player.buy(space)
            await self.write(f"You bought {space.name}")

    async def NONE(self, *data):
        pass

    def __aiter__(self):
        return self

class WSClient(Client):
    def __init__(self, ws):
        self.ws = ws

    @override
    async def read(self, prompt: str) -> str:
        return await self.ws.recv()

    @override
    async def write(self, data: str):
        await self.ws.send(data)

    @override
    async def __anext__(self) -> dict[str, Any]:
        return await self.ws.recv()

class TermClient(Client):
    @override
    async def read(self, prompt: str) -> str:
        return input(prompt)

    @override
    async def write(self, data: str):
        print(data)

    @override
    async def __anext__(self) -> dict[str, Any]:
        return {"action": "start-turn"}
