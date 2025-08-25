type _responses = {
    "board": Board,
    "assignment": string,
    "next-turn": Player,
    "roll": Board,
    "current-space": Space,
    "notification": string
    "new-set": any
    "player-info": Player
    "prompt": string
    "join-game": string
    "player-list": Player[]
    "reconnect": { "name": string, "piece": string }
}
type ServerResponse = { response: infer A extends keyof _responses, value: _responses[A] }

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
    setAmount: number;
    attrs: { [key: string]: any };
    id: string
}
type playerid_t = string | (Object & string)

export interface Player {
    money: number;
    id: playerid_t
    playerNumber: number;
    ownedSpaces: Space[] | [];
    piece: string
    space: Space
    name: string
}

