type ServerResponse = 
| {response: "board", value: Board} 

export interface Board {
    space: Space
    playerSpaces: Record<string, Space>
    spaces: Space[]
}

export interface Space {
    spaceType: number;
    next: Space | null;
    prev: Space | null;
    players: string[];
    cost: number;
    name: string;
    owner: Player | null;
    setAmount: number;
    attrs: { [key: string]: any };
}

export interface Player {
    money: number;
    id: string;
    playerNumber: number;
    ownedSpaces: Space[];
    piece: string
}