import { useContext } from "react";
import MonopolyContext from "../../src/Contexts/MonopolyContext";
import ConnectionContext from "../../src/Contexts/ConnectionContext";
import useWebSocket from "react-use-websocket/dist";
import SimplePlayerCard from "./SimplePlayerCard";



function Lobby() {
    const { players, lobbyState, player } = useContext(MonopolyContext)
    const { ip } = useContext(ConnectionContext)
    const { sendJsonMessage } = useWebSocket(ip, {
        share: true
    })

    return (
        <>
            <div className="lobby-container">
                <div className="player-list">{players.map(p => (
                    <SimplePlayerCard player={p}></SimplePlayerCard>
                ))}</div>
                {lobbyState.host === player.id && <button className="start-button" disabled={players.length < 2} onClick={() => {
                    sendJsonMessage({ "action": "start-game" })
                }}>Start Game</button>}
            </div>

        </>
    )
}

export default Lobby