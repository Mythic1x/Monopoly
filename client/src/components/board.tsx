import { Board, Space } from "../../index";

interface Props {
    board: Board
}

function Space({ space, piece }: { space: Space, piece: string }) {
    console.log(space.attrs)
    return <>
        <div className="space" data-color={space.attrs.color}>
            <span className="name">{space.name}</span>
            <span className="cost">{space.cost}</span>
            <span className="piece">{piece}</span>
            <span className="cost" data-cost={Math.abs(space.cost)} data-earn={space.cost < 0 ? "true" : "false"}></span>
        </div>
    </>
}

function GameBoard({ board }: Props) {
    const colCount = board.spaces.length / 4 + 1
    const rowCount = board.spaces.length / 4 + 1

    let spaces = []
    let row = 0
    let spaceNo = 0

    for (let i = 0; i < colCount * rowCount; i++) {
        let col = i % colCount
        if (i !== 0 && i % colCount === 0) {
            row++
        }
        if (row === 0) {
            const space = board.spaces[spaceNo]
            spaces.push(<Space space={space} piece={space.owner?.piece} />)
            spaceNo++
        } else if (row === rowCount - 1) {
            const space: Space = board.spaces[spaceNo - col * 2 + 1]
            spaces.push(<Space space={space} piece={space.owner?.piece }  />)
            spaceNo++
        } else if (col === colCount - 1) {
            const space = board.spaces[spaceNo - row]
            spaces.push(<Space space={space} piece={space.owner?.piece} />)
            spaceNo++
        } else if (col === 0) {
            const space = board.spaces[spaceNo - row * 3 + ((colCount - 1) * 3 + 1)]
            spaces.push(<Space space={space} piece={space.owner?.piece} />)
            spaceNo++
        } else {
            spaces.push(<div></div>)
        }
    }

    return <>
        <div className="board">
            {spaces}
        </div>
    </>
}

export default GameBoard