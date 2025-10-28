import { Player } from '../../index'

interface Props {
    player: Player
}

export default function SimplePlayerCard({ player }: Props) {
    return <>
        <div className="simple-player-card">
            {
                /*
                    react sucks, put a space at the end of player.name
                    so that there's a fucking space
                */
            }
            <span className='player-name'>{player.name} </span>
            <span className='player-money'>(${player.money})</span>
        </div>
    </>
}
