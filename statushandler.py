from board import Player, Space


class StatusHandler:
    def PROMPT_TO_BUY(player: Player, space: "Space"):
            response = input(f"Buy? it will cost {space.cost}\n")
            if response == "yes": 
                player.buy(space)
                print(f"you bought it!!! you now have {player.money}\nSpaces: {player.ownedSpaces}")