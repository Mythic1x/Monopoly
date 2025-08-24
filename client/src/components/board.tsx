import { Board, Space } from "../../index";

interface Props {
    board: Board
}

function Space({ space }: { space: Space }) {
    console.log(space.attrs)
    return <>
        <div className="space" data-color={space.attrs.color}>
            <span className="name">{space.name}</span>
            <span className="cost">{space.cost}</span>
        </div>
    </>
}

function GameBoard({ board }: Props) {
    const colCount = board.spaces.length / 4 + 1
    const rowCount = board.spaces.length / 4 + 1

    let spaces = []
    let row = 0
    let spaceNo = 0

    for(let i = 0; i < colCount * rowCount; i++) {
        let col = i % colCount
        if (i !== 0 && i % colCount === 0) {
            row++
        }
        if(row === 0) {
            spaces.push(<Space space={board.spaces[spaceNo]} />)
            spaceNo++
        } else if(row === rowCount - 1) {
            spaces.push(<Space space={board.spaces[spaceNo - col * 2 + 1]} />)
            spaceNo++
        } else if(col === colCount - 1) {
            spaces.push(<Space space={board.spaces[spaceNo - row]} />)
            spaceNo++
        } else if(col === 0) {
            spaces.push(<Space space={board.spaces[spaceNo - row * 3 + ((colCount - 1) * 3 + 1)]} />)
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
