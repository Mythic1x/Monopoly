from typing import Any

import board


type token_t = int
T_NAME = 0
T_LC = 1
T_RC = 2
T_EQ = 3
T_SEM = 4
T_ARROW = 5
T_NUMBER = 6
T_LBR = 7
T_RBR = 8
T_ERR = 9

class TokenError(Exception):
    pass

class SyntaxError(Exception):
    pass

class Token[T]:
    value: T
    ty: token_t
    def __init__(self, ty: token_t, value: T) -> None:
        self.value = value
        self.ty = ty

    def __repr__(self):
        return f'{self.ty} : "{self.value}"'

class SpacesLexer:
    text: str
    tokens: list[Token[Any]]

    i: int

    def __init__(self, text: str):
        self.text = text
        self.tokens = []

        self.i = -1

    def isdigit(self, ch: str):
        return ch in "0123456789"

    def next(self):
        self.i += 1
        return self.i < len(self.text)

    def back(self):
        self.i -= 1

    def buildDigit(self, start: str):
        d = start
        while self.next() and self.isdigit(self.text[self.i]):
            d += self.text[self.i]
        self.back()
        return int(d)

    def buildWord(self, start: str):
        w = start
        while self.next() and self.text[self.i].lower() in "abcdefghijklmnopqrstuvwxyz&_. ":
            w += self.text[self.i]
        self.back()
        return w

    def lex(self):
        while self.next():
            ch = self.text[self.i]
            if ch == "=":
                self.tokens.append(Token(T_EQ, '='))
            elif ch == "{":
                self.tokens.append(Token(T_LC, '{'))
            elif ch == "}":
                self.tokens.append(Token(T_RC, '}'))
            elif ch == "[":
                self.tokens.append(Token(T_LBR, '['))
            elif ch == "]":
                self.tokens.append(Token(T_RBR, ']'))
            elif ch == ";":
                self.tokens.append(Token(T_SEM, ';'))
            elif ch == '-':
                if not self.next():
                    self.tokens.append(Token(T_ERR, '-'))
                    break
                elif self.text[self.i] == '>':
                    self.tokens.append(Token(T_ARROW, '->'))
                elif self.isdigit(self.text[self.i]):
                    self.tokens.append(Token(T_NUMBER, self.buildDigit("-" + self.text[self.i])))

            elif self.isdigit(ch):
                self.tokens.append(Token(T_NUMBER, self.buildDigit(ch)))

            elif ch in "\t\n ": continue

            else:
                self.tokens.append(Token(T_NAME, self.buildWord(ch).strip()))

class BoardBuilder:
    tokens: list[Token[Any]]
    spaces: dict[str, board.Space]
    sides: dict[str, board.Space]

    def __init__(self, tokens: list[Token[Any]]):
        self.tokens = tokens
        self.spaces = {}
        self.sides = {}

        self.i = -1

    def next(self):
        self.i += 1
        return self.i < len(self.tokens)

    @property
    def curTok(self):
        return self.tokens[self.i]

    def spaceDefinition(self, name: str):
        attrs: dict[str, Any] = {}

        curAttr = ""
        curValue = None
        while self.next() and self.curTok.ty != T_RC:
            if self.curTok.ty == T_NAME and not curAttr:
                curAttr = self.curTok.value
            elif self.curTok.ty == T_EQ:
                continue
            elif self.curTok.ty == T_SEM:
                attrs[curAttr] = curValue
                curValue = None
                curAttr = ""
            else:
                curValue = self.curTok.value
        spaceTY = str(attrs["type"])
        ty = board.ST_VOID
        match spaceTY.upper():
                case "PROPERTY":
                    ty = board.ST_PROPERTY
                case "COMMUNITY_CHEST":
                    ty = board.ST_COMMUNITY_CHEST
                case "CHANCE":
                    ty = board.ST_CHANCE
                case "JAIL":
                    ty = board.ST_JAIL
                case "GOTO_JAIL":
                    ty = board.ST_GOTO_JAIL
                case "GO":
                    ty = board.ST_GO
                case "ST_LUXURY_TAX":
                    ty = board.ST_LUXURY_TAX
                case "INCOME_TAX":
                    ty = board.ST_INCOME_TAX
                case "RAILROAD":
                    ty = board.ST_RAILROAD

        self.spaces[name] = board.Space(ty, purchaseable="not_purchaseable" not in attrs, name=name, **attrs)


    def spaceOrderDefinition(self, name: str):
        #skip eq
        self.next()

        curSpace = self.spaces[self.curTok.value].copy()
        self.sides[name] = curSpace
        while self.next() and self.curTok.ty == T_ARROW:
            self.next()
            newSpace = self.spaces[self.curTok.value].copy()
            curSpace.setNext(newSpace)
            curSpace = newSpace


    def statement(self):
        name = self.tokens[self.i]
        if name.ty != T_NAME:
            raise TokenError(f"expected NAME token, got {name.value}")

        if not self.next():
            raise SyntaxError(f"Expected '{{' or '=' token after NAME token, got EOF")

        if self.curTok.ty == T_LC:
            self.spaceDefinition(name.value)
        elif self.curTok.ty == T_EQ:
            self.spaceOrderDefinition(name.value)

    def build(self):
        while self.next():
            if self.curTok.ty == T_SEM:
                continue
            self.statement()

        sides = ("start", "left", "top", "right")
        for i, side in enumerate(sides):
            self.sides[side].getLast().setNext(self.sides[sides[(i + 1) % len(sides)]])

def buildFromFile(path: str):
    with open(path) as f:
        data = f.read()
        l = SpacesLexer(data)
        l.lex()
        builder = BoardBuilder(l.tokens)
        builder.build()
        return builder.sides["start"]
