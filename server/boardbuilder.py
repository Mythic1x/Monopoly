import json

import board

def buildFromFile(gameid: float, path: str) -> board.Space:
    with open(path) as f:
        data = json.load(f)
        spacesData = data["spaces"]
        spaces = {}
        for space in spacesData:
            s = spacesData[space]
            attrs = {k: v for k, v in s.items() if k not in ("cost", "not_purchaseable", "type")}
            spaces[space] = board.Space(gameid, getattr(board, f"ST_{s["type"]}"), s.get("cost", 0), space, False if s.get("not_purchaseable") else True, **attrs)

        sideNames = ("start", "left", "top", "right")
        firstSpace = None
        for side in sideNames:
            spaceNames = [x.strip() for x in data[side].split("->")]
            for name in spaceNames:
                if not firstSpace:
                    firstSpace = spaces[name]
                else:
                    firstSpace.getLast().setNext(spaces[name].copy())

        assert firstSpace, "The board has no spaces"
        firstSpace.getLast().setNext(firstSpace)

        return firstSpace
