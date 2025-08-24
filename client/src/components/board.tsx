import { Board, Space } from "../../index";

interface Props {
    board: Board
}

function GameBoard({ board }: Props) {
    return <>
        <div className="board">{board.spaces.map((space: Space) =>
            <div className="space">
                <span className="name">{space.name}</span>
                <span className="cost">{space.cost}</span>
            </div>
        )}</div>
    </>
}

export default GameBoard