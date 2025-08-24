import { useState, useEffect } from "react"
import { Board, Space, Player, ServerResponse } from "../../index"
import useWebSocket, { ReadyState } from "react-use-websocket/dist"
import usePlayer from "../hooks/useplayer"
import GameBoard from "./board"

function Monopoly({ playerDetails }: any) {
    const [rolled, setRolled] = useState<boolean>(false)
    const [board, setBoard] = useState<Board | null>(null)
    const [loading, setLoading] = useState(true)
    const [currentSpace, setCurrentSpace] = useState<Space | null>(null)
    const [goingPlayer, setGoingPlayer] = useState<Player | null>(null)
    const { sendJsonMessage, lastJsonMessage, readyState, } = useWebSocket("ws://localhost:8765", {
        share: true
    })
    const { player, playerLoaded } = usePlayer()

    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            sendJsonMessage({ "action": "set-details", "details": playerDetails })
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
        }
    }, [lastJsonMessage])


    if (loading || !playerLoaded) {
        return <>
            <span className="loading">loading...</span></>
    }

    return <>
        <div className="board-container">
            <GameBoard board={board}></GameBoard>
            <button className="roll" disabled={goingPlayer?.id !== player.id || rolled} onClick={() => {
                sendJsonMessage({ "action": "roll" })
                setRolled(true)
            }}>Roll</button>
        </div>
        {(goingPlayer?.id === player.id) && <button className="buy" disabled={!!currentSpace?.owner} onClick={() => {
            sendJsonMessage({ "action": "buy", "property": currentSpace.id })
        }}>Buy Property</button>
        }
        <button className="end-turn" disabled={goingPlayer?.id !== player.id} onClick={() => {
            sendJsonMessage({ "action": "end-turn" })
            setRolled(false)
        }}>End Turn</button>
    </>
}

export default Monopoly