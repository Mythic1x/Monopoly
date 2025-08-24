import { useEffect, useState } from 'react';
import { ServerResponse, Space, Board, Player } from '../index'
import useWebSocket, { ReadyState } from 'react-use-websocket';
import GameBoard from './components/board';

function App() {
    const [board, setBoard] = useState<Board | null>(null)
    const [loading, setLoading] = useState(true)
    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket("ws://localhost:8765", {
        share: true
    })

    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            sendJsonMessage({ 'action': "connect" })
            console.log("connected to socket")
        }
        console.log("not ready")
    }, [readyState])

    useEffect(() => {
        const message = lastJsonMessage as ServerResponse
        console.log(message)
        if(!message) return
        switch (message.response) {
            case "board":
                console.log()
                setBoard(message.value)
                setLoading(false)
        }
    }, [lastJsonMessage])

    if (loading) {
        return <>
            <span className="loading">loading...</span></>
    }

    return <>
        <div className="board-container">
            <GameBoard board={board}></GameBoard>
        </div>
    </>
}

export default App