import { useEffect, useState, useRef } from "react"
import { Player } from "../../index"
interface Props {
    player: Player
    goingPlayer: Player
}

export default function PlayerCard({ player, goingPlayer }: Props) {
    const flash = flashWhenChange(player.money)

    return (
        <>
            <div className="player-card-container">
                <div className="player-card" data-color={player.color}>
                    <div className="player-name">{player.name}</div>
                    <div className={`player-money ${flash === "decrease" ? "flash-red" : ""} ${flash === "increase" ? "flash-green" : ""}`} style={{ color: player.money < 0 ? "red" : "" }}>{player.bankrupt ? "bankrupt" : `$${player.money}`}</div>
                    <div className="player-credit-score">{player.bankrupt ? "bankrupt" : `Credit Score: ${player.creditScore}`}</div>
                    <div className="owned-spaces-count">{player.bankrupt ? "bankrupt" : `Owned Spaces: ${player.ownedSpaces?.length ?? 0}`}</div>
                </div>
                {goingPlayer?.id === player.id && <span className="turn-indicator">🎲</span>}
            </div >
        </>
    )
}

function flashWhenChange(value: number) {
    const [flash, setFlashType] = useState<"increase" | "decrease" | false>(false)
    const ref = useRef(value)
    useEffect(() => {
        if (ref.current !== value) {
            const type = ref.current > value ? "decrease" : "increase"
            setFlashType(type)
            setTimeout(() => setFlashType(false), 1000)
            ref.current = value
        }
    }, [value])
    return flash
}

