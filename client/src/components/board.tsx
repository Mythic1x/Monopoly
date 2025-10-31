import { useContext, useRef } from "react";
import { Board, Player, Space } from "../../index";
import SpaceCard from "./SpaceCard";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

interface Props {
    board: Board
    player: Player
    players: Player[]
    children?: React.ReactNode
}

type Logo = "QUESTION_MARK" | "CHEST"

function logo2img(logo: Logo) {
    switch (logo) {
        case "QUESTION_MARK":
            return "https://static.seceurity.place/assets/monopoly/chance.png"
        case "CHEST":
            return "https://static.seceurity.place/assets/monopoly/community_chest.webp"
    }
}

function getLogoSize(logo: Logo) {
    switch (logo) {
        case "QUESTION_MARK":
            return "50%"
        case "CHEST":
            return "50%"
    }
}

function renderSpaceNameFromSpace(space: Space) {
    if (space.attrs.logo) {
        return <img src={logo2img(space.attrs.logo)} width={getLogoSize(space.attrs.logo)} />
    }
    return <span className="name">{space.name}</span>
}

function BoardSpace({ space, player}: { space: Space, player: Player }) {
    const { players } = useContext(MonopolyContext)
    const spaceRef = useRef<HTMLDivElement>(null)

    return <>
        <div className="space" ref={spaceRef} data-owner-color={players.find(p => p.id === space.owner)?.color || "transparent"} data-house-count={space.houses} data-has-hotel={space.hotel} data-anchor-name={`--space-${space.id}`} data-color={space.attrs.color} onClick={() => console.log(space.id)}>
            {space.purchaseable && <SpaceCard space={space} player={player} />}
            {renderSpaceNameFromSpace(space)}
            <span className="cost" data-cost={Math.abs(space.cost)} data-earn={space.cost < 0 ? "true" : "false"}></span>
        </div>
    </>

}

function GameBoard({ board, player, players, children}: Props) {
    const colCount = board.spaces.length / 4 + 1
    const rowCount = board.spaces.length / 4 + 1

    let spaces = []
    let row = 0
    let spaceNo = 0

    for (let i = 0; i < colCount * rowCount; i++) {
        let col = i % colCount
        if (i !== 0 && col === 0) {
            row++
        }
        if (row === 0) {
            const space = board.spaces[spaceNo]
            spaces.push(<BoardSpace space={space} player={player}/>)
            spaceNo++
        } else if (row === rowCount - 1) {
            const space: Space = board.spaces[spaceNo - col * 2 + 1]
            spaces.push(<BoardSpace space={space} player={player}/>)
            spaceNo++
        } else if (col === colCount - 1) {
            const space = board.spaces[spaceNo - row]
            spaces.push(<BoardSpace space={space} player={player} key={space.id}/>)
            spaceNo++
        } else if (col === 0) {
            const space = board.spaces[spaceNo - row * 3 + ((colCount - 1) * 3 + 1)]
            spaces.push(<BoardSpace space={space} player={player} />)
            spaceNo++
        } else {
            spaces.push(<div></div>)
        }
    }

    return <>
        <div className="board">
            {spaces}
            {children}
            <span>
            {players.map(p => 
                <span className="piece" data-current-space={`--space-${p.space}`}>{p.piece}</span>
            )}
            </span>
        </div>
    </>
}

export default GameBoard
