import { useEffect, useState } from 'react';
import { ServerResponse, Space, Board, Player } from '../index'
import useWebSocket, { ReadyState } from 'react-use-websocket';
import GameBoard from './components/board';


function App() {
    const [rolled, setRolled] = useState<boolean>(false)
    const [board, setBoard] = useState<Board | null>(null)
    const [loading, setLoading] = useState(true)
    const [playerId, setPlayerId] = useState<string | null>(null)
    const [currentSpace, setCurrentSpace] = useState<Space | null>(null)
    const [goingPlayer, setGoingPlayer] = useState<Player | null>(null)
    const { sendJsonMessage, lastJsonMessage, readyState, sendMessage } = useWebSocket("ws://localhost:8765", {
        share: true
    })

    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            sendJsonMessage({ 'action': "connect" })
            sendJsonMessage({ 'action': "current-space" })
            console.log("connected to socket")
        }
    }, [readyState])

    useEffect(() => {
        const message = lastJsonMessage as ServerResponse
        if (!message) return
        switch (message.response) {
            case "board":
                setBoard(message.value)
                setLoading(false)
                break
            case 'assignment':
                setPlayerId(message.value)
                break
            case 'current-space':
                setCurrentSpace(message.value)
                break
            case 'next-turn':
                setGoingPlayer(message.value)
                break
            case 'new-set':
                const [color, player] = message.value.split(";")
                alert(`${player} achieved the set for ${color}`)
            case "notification":
                alert(message.value)
                break
            case "prompt": {
                let options = message.value.match(/\([^)]+\)$/)
                console.log(options)
                if(options) {
                    let optionsList = options[0].split("/")
                    alert(`${message.value.replace(options, "")} ${optionsList.join("\n")}`)
                    //prompt with options
                } else {
                    //regular prompt
                    alert(message.value)
                }
                break
            }
        }
    }, [lastJsonMessage])


    if (loading) {
        return <>
            <span className="loading">loading...</span></>
    }

    return <>
        <div className="board-container">
            <GameBoard board={board}></GameBoard>
            <button className="roll" disabled={goingPlayer?.id !== playerId || rolled} onClick={() => {
                sendJsonMessage({ "action": "roll" })
                setRolled(true)
            }}>Roll</button>
        </div>
        <button className="end-turn" disabled={goingPlayer?.id !== playerId} onClick={() => {
            sendJsonMessage({ "action": "end-turn" })
            setRolled(false)
        }}>End Turn</button>
    </>
}

export default App
