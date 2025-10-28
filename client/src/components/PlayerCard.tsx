import { Player } from "../../index"
interface Props {
    player: Player
}

export default function PlayerCard({ player }: Props) {
    return (
        <>
            <div className="player-card" data-color={player.color}>
                <div className="player-name">{player.name}</div>
                <div className="player-money">{player.bankrupt ? "bankrupt" : `$${player.money}`}</div>
                <div className="owned-spaces-count">{player.bankrupt ? "bankrupt" : `Owned Spaces: ${player.ownedSpaces?.length ?? 0}`}</div>
            </div>
        </>
    )
}
