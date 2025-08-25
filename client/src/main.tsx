import { FormEvent, useEffect, useState } from 'react';
import { ServerResponse, Space, Board, Player } from '../index'
import useWebSocket, { ReadyState } from 'react-use-websocket';
import GameBoard from './components/board';
import usePlayer from './hooks/useplayer';
import Monopoly from './components/Monopoly';
import PlayerSetup from './components/PlayerSetup';


function App() {
    const [playerDetails, setPlayerDetails] = useState(null)
    const { lastJsonMessage, readyState, } = useWebSocket("ws://localhost:8765", {
        share: true
    })
    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            const message = lastJsonMessage as ServerResponse
            if (message?.response === "reconnect") {
                setPlayerDetails(message.value)
            }
        }
    }, [lastJsonMessage, readyState])
    if (playerDetails) {
        return <>
            <Monopoly playerDetails={playerDetails} ></Monopoly>
        </>
    } else {
        return <PlayerSetup onSetupComplete={setPlayerDetails}></PlayerSetup>
    }

}

export default App
