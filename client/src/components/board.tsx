import { Board, Space } from "../../index";

interface Props {
    board: Board
}

function Space({ space, piece }: { space: Space, piece: string }) {
    return <>
        <div className="space">
            <span className="name">{space.name}</span>
            <span className="cost">{space.cost}</span>
            <span className="piece">{piece}</span>
        </div>
    </>
}

function GameBoard({ board }: Props) {
    const spaces = board.spaces.map((space: Space, index) => {
        return <Space space={space}
            piece={space.owner ? space.owner.piece : null} key={index}
        ></Space>
    })
    return <>
        <div className="board">
            <div className="bottom">{spaces.slice(0, 10)}</div>
            <div className="left">{spaces.slice(10, 20)}</div>
            <div className="top">{spaces.slice(20, 30)}</div>
            <div className="right">{spaces.slice(30)}</div>
        </div>
    </>
}

export default GameBoard
