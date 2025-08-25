import { Player } from "../../index"
interface Props {
    player: Player
}
export default function PlayerCard({ player }: Props) {
    return (
        <>
        <div className="player-card"></div>
        <div className="player-name">{player.name}</div>
        <div className="player-money">Money: {player.money}</div>
        <div className="owned-spaces-count">Owned Spaces: {player.ownedSpaces?.length ?? 0}</div>
        </>
    )
}