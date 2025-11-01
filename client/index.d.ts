
type _responses = {
    "board": Board,
    "assignment": string,
    "next-turn": Player,
    "roll": Board,
    "current-space": Space,
    "notification": string | null
    "new-set": any
    "player-info": Player
    "prompt": string
    "join-game": string
    "player-list": Player[]
    "loan-list": Loan[]
    "trade-list": Trade[]
    "reconnect": { "name": string, "piece": string }
    "trade-proposal": Trade
    "auction-status": Auction
    "auction-end": any
    "turn-ended": Player
    "roll-complete": null
    "bankrupt": string
    "game-end": Player
    "loan-proposal": Loan
    "lobby-state": LobbyState
}
type ServerResponse = { response: infer A extends keyof _responses, value: _responses[A] } | { response: infer A extends keyof _responses, value: _responses[A] }[]

type Trade = {
    trade: {
        want: {
            properties: number[],
            money: number
        },
        give: {
            properties: number[]
            money: number
        }
    }
    sender: string
    recipient: string
    status: "declined" | "accepted" | "proposed"
    id?: number

}

export interface Auction {
    current_bid: number
    bidder: playerid_t
    end_time: number
    space: spaceid_t
}

export interface LobbyState {
    host: playerid_t
    started: boolean
}

export interface Board {
    space: Space
    playerSpaces: Record<string, Space>
    spaces: Space[]
}

export interface Space {
    spaceType: number;
    next: Space | null;
    prev: Space | null;
    players: Player[];
    cost: number;
    name: string;
    owner: playerid_t | null;
    attrs: { [key: string]: any };
    id: spaceid_t
    houseCost: number
    houses: number
    hotel: boolean
    purchaseable: boolean
    mortgaged: boolean
}

type playerid_t = string | (Object & string)
type spaceid_t = number | (Object & number)

export interface Player {
    money: number;
    id: playerid_t
    playerNumber: number;
    ownedSpaces: Space[] | [];
    piece: string
    space: spaceid_t
    name: string
    sets: Color[]
    bankrupt: boolean
    injail: boolean
    loans: Loan[]
    color: string
    creditScore: number
}

export type Color =
    | "brown"
    | "lightblue"
    | "pink"
    | "orange"
    | "red"
    | "yellow"
    | "green"
    | "blue"


export interface Loan {
    type: "per-turn" | "deadline"
    amountPerTurn: number | null
    deadline: number | null
    amount: number
    interest: number
    interestType: "simple" | "compound"
    loanee: str
    loaner: str | null
    status: "declined" | "accepted" | "proposed"
    id?: string
    turnsPassed?: number
    remainingToPay?: number
}


declare global {
    interface Window {
        BOARD: Board
        findSpaceByName: (name: string) => Space | null,
        me: Player
    }
}
