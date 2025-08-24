import { Board, Space } from "../../index";

interface Props {
    board: Board
}

function Space({ space }: { space: Space }) {
    return <>
        <div className="space">
            <span className="name">{space.name}</span>
            <span className="cost">{space.cost}</span>
        </div>
    </>
}

function GameBoard({ board }: Props) {
    console.log(board)
    return <>
        <div className="board">
            <div className="bottom">{board.spaces.slice(0, 10).map(space => <Space space={space} />)}</div>
            <div className="left">{board.spaces.slice(10, 20).map(space => <Space space={space} />)}</div>
            <div className="top">{board.spaces.slice(20, 30).map(space => <Space space={space} />)}</div>
            <div className="right">{board.spaces.slice(30).map(space => <Space space={space} />)}</div>
        </div>
    </>
}

export default GameBoard
