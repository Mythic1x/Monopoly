import { useContext, useEffect, useRef } from "react";
import { Board, Player, Space, spaceid_t } from "../../index";
import SpaceCard from "./SpaceCard";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

interface Props {
    board: Board
    player: Player
    children?: React.ReactNode
    setSpaceCoordinates: setSpaceCoordinates
}

type setSpaceCoordinates = React.Dispatch<React.SetStateAction<{
    [key: spaceid_t]: {
        x: number;
        y: number;
    };
}>>

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

function BoardSpace({ space, pieces, player, setSpaceCoordinates }: { space: Space, pieces: string[], player: Player, setSpaceCoordinates: setSpaceCoordinates }) {
    const { players } = useContext(MonopolyContext)
    const spaceRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (spaceRef.current) {
            const rect = spaceRef.current.getBoundingClientRect()
            setSpaceCoordinates(o => ({
                ...o,
                [space.id]: { x: rect.x, y: rect.y }
            }))
        }

    }, [])

    return <>
        <div className="space" ref={spaceRef} data-owner-color={players.find(p => p.id === space.owner)?.color || "transparent"} data-house-count={space.houses} data-has-hotel={space.hotel} data-anchor-name={`--space-${space.id}`} data-color={space.attrs.color} onClick={() => console.log(space.id)}>
            {space.purchaseable && <SpaceCard space={space} player={player} />}
            {renderSpaceNameFromSpace(space)}
            <span className="cost" data-cost={Math.abs(space.cost)} data-earn={space.cost < 0 ? "true" : "false"}></span>
            <span className="pieces">{pieces.map(piece => (
                <span className="piece">{piece}</span>
            ))}</span>
        </div>
    </>

}

function GameBoard({ board, player, children, setSpaceCoordinates }: Props) {
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
            spaces.push(<BoardSpace space={space} player={player} setSpaceCoordinates={setSpaceCoordinates} pieces={space.players.map((player) => (
                player.piece
            ))} />)
            spaceNo++
        } else if (row === rowCount - 1) {
            const space: Space = board.spaces[spaceNo - col * 2 + 1]
            spaces.push(<BoardSpace space={space} player={player} setSpaceCoordinates={setSpaceCoordinates} pieces={space.players.map((player) => (
                player.piece
            ))} />)
            spaceNo++
        } else if (col === colCount - 1) {
            const space = board.spaces[spaceNo - row]
            spaces.push(<BoardSpace space={space} player={player} key={space.id} setSpaceCoordinates={setSpaceCoordinates} pieces={space.players.map((player) => (
                player.piece
            ))} />)
            spaceNo++
        } else if (col === 0) {
            const space = board.spaces[spaceNo - row * 3 + ((colCount - 1) * 3 + 1)]
            spaces.push(<BoardSpace space={space} player={player} setSpaceCoordinates={setSpaceCoordinates} pieces={space.players.map((player) => (
                player.piece
            ))} />)
            spaceNo++
        } else {
            spaces.push(<div></div>)
        }
    }

    return <>
        <div className="board">
            {spaces}
            {children}
        </div>
    </>
}

export default GameBoard
