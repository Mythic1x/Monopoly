import { useState, useEffect, useRef } from "react"
import { Board, Space, Player, ServerResponse, Trade } from "../../index"
import PlayerCard from "./PlayerCard"
import useWebSocket, { ReadyState } from "react-use-websocket/dist"
import usePlayer from "../hooks/useplayer"
import GameBoard from "./board"
import { socketAddr } from "../../socket"
import Alert from "./alert"
import TradeMenu from "./TradeMenu"

function Monopoly({ playerDetails }: any) {
    const [alertQ, setAQ] = useState<string[]>([])

    const tradeDialog = useRef<HTMLDialogElement>(null)

    const [currentTrade, setCurrentTrade] = useState<Trade | null>(null)

    const [rolled, setRolled] = useState<boolean>(false)
    const [players, setPlayers] = useState<Player[] | []>([])
    const [board, setBoard] = useState<Board | null>(null)
    const [loading, setLoading] = useState(true)
    const [currentSpace, setCurrentSpace] = useState<Space | null>(null)
    const [goingPlayer, setGoingPlayer] = useState<Player | null>(null)
    const { sendJsonMessage, lastJsonMessage, readyState, } = useWebSocket(socketAddr, {
        share: true
    })
    const { player, playerLoaded } = usePlayer()

    window["findSpaceByName"] = (name: string) => {
        for (let space of board.spaces) {
            if (space.name.toLowerCase() === name.toLowerCase()) {
                return space
            }
        }
    }
    window["me"] = player

    function alert(text: string) {
        setAQ(alertQ.concat([text]))
    }

    useEffect(() => {
        const id = setInterval(() => {
            alertQ.shift()
            setAQ(alertQ)
        }, 2500)
        return () => clearInterval(id)
    }, [])

    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            sendJsonMessage({ "action": "set-details", "details": playerDetails })
        }
    }, [readyState])


    useEffect(() => {
        let messages = lastJsonMessage as ServerResponse
        if (!messages) return
        for (let message of Array.isArray(messages) ? messages : [messages]) {
            switch (message.response) {
                case "player-list":
                    setPlayers(message.value)
                    break
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
                case "join-game":
                    sendJsonMessage({ 'action': "connect" })
                    sendJsonMessage({ 'action': "current-space" })
                    break
                case "trade-proposal":
                    console.log(message.value)
                    tradeDialog.current.showModal()
                    setCurrentTrade(message.value)
                    break
            }
        }
    }, [lastJsonMessage])


    if (loading || !playerLoaded) {
        return <>
            <span className="loading">loading...</span></>
    }

    return <>
        <TradeMenu players={players} tradeDialog={tradeDialog} currentTrade={currentTrade}></TradeMenu>

        <div id="game">
            <div className="board-container">
                <GameBoard board={board} player={player}>
                    <div className="alert-container">
                        {alertQ.map(v => <Alert alert={v} />)}
                    </div>
                    <div className="button-container">
                        <button className="roll" disabled={goingPlayer?.id !== player.id || rolled} onClick={() => {
                            sendJsonMessage({ "action": "roll" })
                            setRolled(true)
                        }}>Roll</button>
                        {(goingPlayer?.id === player.id) && <button className="buy" disabled={!!currentSpace?.owner || !currentSpace.purchaseable} onClick={() => {
                            sendJsonMessage({ "action": "buy", "spaceid": currentSpace.id })
                        }}>Buy Property</button>
                        }
                        <button className="end-turn" disabled={goingPlayer?.id !== player.id || !rolled} onClick={() => {
                            sendJsonMessage({ "action": "end-turn" })
                            setRolled(false)
                        }}>End Turn</button>
                        <button onClick={() => sendJsonMessage({ "action": "propose-trade", "trade": { "give": { "money": 10 }, "want": {} }, "playerid": player.id })} >
                            Trade
                        </button>
                    </div>
                </GameBoard>

            </div>
            <div className="player-list">
                <h3>Players</h3>
                {players?.map((player) => (
                    <PlayerCard player={player}></PlayerCard>
                ))}
            </div>
        </div>
    </>
}

export default Monopoly
