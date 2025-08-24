type ServerResponse =
  | { response: "board"; value: Board }
  | { response: "assignment"; value: string }
  | { response: "next-turn"; value: Player }
  | { response: "roll"; value: Board }
  | {response: "current-space"; value: Space}
  | {response: "notification"; value: string}

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
    owner: Player | null;
    setAmount: number;
    attrs: { [key: string]: any };
    id: string
}

export interface Player {
    money: number;
    id: string;
    playerNumber: number;
    ownedSpaces: Space[];
    piece: string
    space: Space
}

