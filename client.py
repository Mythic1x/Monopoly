import abc
import json
from typing import Any, Self, override

from board import Player, Space, status_t, PROMPT_TO_BUY, MONEY_LOST, PAY_JAIL, BUY_SUCCESS, BUY_HOTEL_SUCCESS, BUY_HOUSE_SUCCESS, BUY_FAIL, BUY_HOUSE_FAIL, BUY_HOTEL_FAIL, BUY_NEW_SET, MONEY_GIVEN, PAY_OTHER, PAY_TAX, PASS_GO, NONE, DRAW_CHANCE, FAIL, MORTGAGE_SUCCESS, UNMORTGAGE_SUCCESS, BANKRUPT, DUE_LOAN
    
class Client(abc.ABC):
    @abc.abstractmethod
    async def read(self, prompt: str) -> str: ...

    @abc.abstractmethod
    async def write(self, data: dict | list[dict]): ...

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
    async def write(self, data: dict | list[dict]):
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
    async def write(self, data: dict | list[dict]):
        print(data)

    @override
    async def __anext__(self) -> dict[str, Any]:
        res = input("> ")
        if res == "end-turn":
            return {"action": "end-turn"}
        return {"action": "start-turn"}
