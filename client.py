import abc
import json
from typing import Any, Self, override

from board import Player, Space, status_t, PROMPT_TO_BUY, MONEY_LOST, PAY_JAIL, BUY_SUCCESS, BUY_HOTEL_SUCCESS, BUY_HOUSE_SUCCESS, BUY_FAIL, BUY_HOUSE_FAIL, BUY_HOTEL_FAIL, BUY_NEW_SET, MONEY_GIVEN, PAY_OTHER, PAY_TAX, PASS_GO, NONE
    
class Client(abc.ABC):
    @abc.abstractmethod
    async def read(self, prompt: str) -> str: ...

    @abc.abstractmethod
    async def write(self, data: dict | list[dict]): ...

    @abc.abstractmethod
    async def __anext__(self) -> dict[str, Any]: ...

    async def handleStatus(self, status: status_t, player: Player):
        status = await getattr(self, status.__class__.__name__)(player, status)
        return status

    def mknotif(self, text: str):
        return { "response": "notification", "value": text}

    async def PROMPT_TO_BUY(self, player: Player, status: PROMPT_TO_BUY):
        await self.write({"response": "notification", "value": f"{status.space.name} is available for purchase for the price of ${status.space.cost}"})

    async def MONEY_LOST(self, player: Player, status: MONEY_LOST):
        await self.write({"response": "notification", "value": f"{player.name} lost {status.amount}"})

    async def PAY_JAIL(self, player: Player, status: PAY_JAIL):
        await self.write(self.mknotif(f"{player.name} paid ${status.cost} to get out of jail"))

    async def BUY_SUCCESS(self, player: Player, status: BUY_SUCCESS):
        await self.write({"response": "notification", "value": f"{player.name} successfully bought {status.space.name}"})
        
    async def BUY_HOUSE_SUCCESS(self, player: Player, status: BUY_HOUSE_SUCCESS):
        await self.write({"response": "notification", "value": f"{player.name} bought a house on {status.space.name}"})
        
    async def BUY_HOTEL_SUCCESS(self, player: Player, status: BUY_HOTEL_SUCCESS):
        await self.write({"response": "notification", "value": f"{player.name} bought a hotel on {status.space.name}"})

    async def BUY_FAIL(self, player: Player, status: BUY_FAIL):
        await self.write({"response": "notification", "value": f"{player.name} failed"})
        
    async def BUY_HOUSE_FAIL(self, player: Player, status: BUY_HOUSE_FAIL):
        await self.write({"response": "notification", "value": f"{player.name} failed to purchase house on {status.space.name}"})

    async def BUY_HOTEL_FAIL(self, player: Player, status: BUY_HOTEL_FAIL):
        await self.write({"response": "notification", "value": f"{player.name} failed to purchase hotel on {status.space.name}"})
        
    async def BUY_NEW_SET(self, player: Player, status: BUY_NEW_SET):
        await self.write({"response": "notification", "value": f"{player.name} successfully bought {status.space.name} for a complete {status.space.color} set"})

    async def MONEY_GIVEN(self, player: Player, status: MONEY_GIVEN):
        await self.write({"response": "notification", "value": f"{player.name} gained {status.amount}"})

    async def PAY_OTHER(self, player: Player, status: PAY_OTHER):
        await self.write(self.mknotif(f"{player.name} paid {status.other.name} ${status.amount}"))

    async def PAY_TAX(self, player: Player, status: PAY_TAX):
        await self.write(self.mknotif(f"{player.name} paid {status.amount} in {status.taxname} taxes"))
        
    async def AUCTION_END(self, winner: Player, space: Space):
        await self.write({"response": "notification", "value": f"{winner.name} won {space.name} in an auction!"})

    async def PASS_GO(self, player: Player, status: PASS_GO):
        await self.write(self.mknotif(f"{player.name} passed go and got ${status.earned}"))

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
    async def write(self, data: dict | list[dict]):
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
    async def write(self, data: dict | list[dict]):
        print(data)

    @override
    async def __anext__(self) -> dict[str, Any]:
        res = input("> ")
        if res == "end-turn":
            return {"action": "end-turn"}
        return {"action": "start-turn"}
