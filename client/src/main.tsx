import { useEffect, useState } from 'react';
import { ServerResponse, Space, Board, Player } from '../index'
import useWebSocket, { ReadyState } from 'react-use-websocket';

function App() {
    const [board, setBoard] = useState<Board | null>(null)
    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket("ws://localhost:8765", {
        share: true
    })  

    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            sendJsonMessage({ 'action': "connect" })
        }
    }, [readyState])

    useEffect(() => {
        const message = lastJsonMessage as ServerResponse
        switch (message.response) {
            case "board":
                setBoard(message.value)
        }
    }, [lastJsonMessage, sendJsonMessage])

    return <>
        <div className="board-container">
            <div className="board"></div>
        </div>
    </>
}

export default App