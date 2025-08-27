import { FormEvent, useEffect, useState } from 'react';
import { ServerResponse, Space, Board, Player } from '../index'
import useWebSocket, { ReadyState } from 'react-use-websocket';
import GameBoard from './components/board';
import usePlayer from './hooks/useplayer';
import Monopoly from './components/Monopoly';
import PlayerSetup from './components/PlayerSetup';
import { socketAddr } from '../socket'
import { MonopolyProvider } from './Contexts/MonopolyContext';


function App() {

    const [playerDetails, setPlayerDetails] = useState(null)
    const { lastJsonMessage, readyState, } = useWebSocket(socketAddr, {
        share: true
    })
    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            const message = lastJsonMessage as ServerResponse
            if (Array.isArray(message)) {
                if (message[0]?.response === "reconnect") {
                    setPlayerDetails(message[0].value)
                }
            } else {
                if (message?.response === "reconnect") {
                    setPlayerDetails(message.value)
                }
            }
        }
    }, [lastJsonMessage, readyState])
    if (playerDetails) {
        return <>
            <MonopolyProvider>
                <Monopoly playerDetails={playerDetails} ></Monopoly>
            </MonopolyProvider>
        </>
    } else {
        return <PlayerSetup onSetupComplete={setPlayerDetails}></PlayerSetup>
    }

}

export default App
