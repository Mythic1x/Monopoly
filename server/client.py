import abc
import json
from typing import Any, override

class Client(abc.ABC):
    @abc.abstractmethod
    async def read(self, prompt: str) -> str: ...

    @abc.abstractmethod
    async def write(self, data: dict[Any, Any] | list[dict[Any, Any]]): ...

    @abc.abstractmethod
    async def __anext__(self) -> dict[str, Any]: ...

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
    async def write(self, data: dict[Any, Any] | list[dict[Any, Any]]):
        await self.ws.send(json.dumps(data))
    
    @override
    async def __anext__(self) -> dict[str, Any]:
        return json.loads(await self.ws.recv())

class TermClient(Client):

    # @override
    # async def handleStatus(self, status: str, player: Player, data: list[Any]):
    #     val = await super().handleStatus(status, player, data)
    #     return val

    @override
    async def read(self, prompt: str) -> str:
        return input(prompt)

    @override
    async def write(self, data: dict[Any, Any] | list[dict[Any, Any]]):
        print(data)

    @override
    async def __anext__(self) -> dict[str, Any]:
        res = input("> ")
        if res == "end-turn":
            return {"action": "end-turn"}
        return {"action": "start-turn"}
