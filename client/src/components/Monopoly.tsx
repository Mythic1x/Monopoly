import { useState, useEffect, useRef, useContext } from "react"
import { Board, Space, Player, ServerResponse, Trade, Auction } from "../../index"
import PlayerCard from "./PlayerCard"
import useWebSocket, { ReadyState } from "react-use-websocket/dist"
import usePlayer from "../hooks/useplayer"
import GameBoard from "./board"
import { socketAddr } from "../../socket"
import Alert from "./alert"
import TradeMenu from "./TradeMenu"
import MonopolyContext, { MonopolyProvider } from "../../src/Contexts/MonopolyContext"
import AuctionMenu from "./Auction"

function Monopoly({ playerDetails }: any) {
    const [alertQ, setAQ] = useState<string[]>([])

    const rollBtn = useRef<HTMLButtonElement>(null)
    const buyBtn = useRef<HTMLButtonElement>(null)
    const auctionBtn = useRef<HTMLButtonElement>(null)

    const tradeDialog = useRef<HTMLDialogElement>(null)

    const [currentTrade, setCurrentTrade] = useState<Trade | null>(null)
    const [auction, setAuction] = useState<Auction | null>(null)

    const { board, player, players, setBoard, setPlayers, playerLoaded, setPlayer } = useContext(MonopolyContext)

    const [rolled, setRolled] = useState<boolean>(false)
    const [loading, setLoading] = useState(true)
    const [currentSpace, setCurrentSpace] = useState<Space | null>(null)
    const [goingPlayer, setGoingPlayer] = useState<Player | null>(null)
    const { sendJsonMessage, lastJsonMessage, readyState, } = useWebSocket(socketAddr, {
        share: true
    })

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
            setAQ(q => q.slice(1))
        }, 2500)
        return () => clearInterval(id)
    }, [])

    useEffect(() => {
        if (readyState === ReadyState.OPEN) {
            sendJsonMessage({ "action": "set-details", "details": playerDetails })
        }
    }, [readyState])

    function endTurn() {
        sendJsonMessage({ "action": "end-turn" })
    }

    useEffect(() => {
        function handleKeys(e: KeyboardEvent) {
            switch (e.key) {
                case "r":
                    rollBtn.current.click()
                    break
                case "e":
                    endTurn()
                    break
                case "b":
                    buyBtn.current.click()
                    break
                case "a":
                    auctionBtn.current.click()
                    break
            }
        }
        addEventListener("keypress", handleKeys)
        return () => removeEventListener("keypress", handleKeys)
    }, [])

    useEffect(() => {
        let messages = lastJsonMessage as ServerResponse
        if (!messages) return
        for (let message of Array.isArray(messages) ? messages : [messages]) {
            switch (message.response) {
                case "player-list": {
                    if (playerLoaded)
                        for (let p of message.value as Player[]) {
                            if (p.id === player.id) {
                                setPlayer(p)
                                setCurrentSpace(board.playerSpaces[p.id])
                            }
                        }
                    setPlayers(message.value)
                    break
                }
                case "board":
                    setBoard(message.value)
                    setLoading(false)
                    break
                case 'current-space':
                    setCurrentSpace(message.value)
                    break
                case "turn-ended":
                    setRolled(false)
                    break
                case "roll-complete":
                    setRolled(true)
                    break
                case 'next-turn':
                    setGoingPlayer(message.value)
                    break
                case 'new-set': {
                    const [color, player] = message.value.split(";")
                    alert(`${player} achieved the set for ${color}`)
                }
                case "notification":
                    alert(message.value)
                    break
                case "join-game":
                    sendJsonMessage({ 'action': "connect" })
                    sendJsonMessage({ 'action': "current-space" })
                    break
                case "trade-proposal":
                    setCurrentTrade(message.value)
                    tradeDialog.current.showModal()
                    break
                case "auction-status":
                    setAuction(message.value)
                    break
                case "auction-end":
                    setAuction(null)
                    break
            }
        }
    }, [lastJsonMessage])


    if (loading || !playerLoaded) {
        return <span className="loading">loading...</span>
    }

    let jail = board.spaces.find(v => v.name === "Jail")
    return <>
        <TradeMenu currentPlayer={player} players={players} tradeDialog={tradeDialog} currentTrade={currentTrade} setCurrentTrade={setCurrentTrade}></TradeMenu>
        <div id="game">
            <div className="board-container">
                <GameBoard board={board} player={player}>
                    {auction &&
                        <AuctionMenu space={currentSpace} time={auction.end_time} auction={auction} sendJsonMessage={sendJsonMessage}></AuctionMenu>
                    }
                    <div id="alert-container">
                        {alertQ.map(v => <Alert alert={v} />)}
                    </div>
                    <div className="button-container">
                        <button ref={rollBtn} className="roll" disabled={goingPlayer?.id !== player.id || rolled || (auction ? true : false)} onClick={() => {
                            sendJsonMessage({ "action": "roll" })
                        }}>Roll</button>
                        {(goingPlayer?.id === player.id) && <button ref={buyBtn} className="buy" disabled={!!currentSpace?.owner || !currentSpace?.purchaseable || player.money < currentSpace.cost} onClick={() => {
                            sendJsonMessage({ "action": "buy", "spaceid": currentSpace.id })
                        }}>Buy Property</button>
                        }
                        <button className="end-turn" disabled={goingPlayer?.id !== player.id || !rolled || (auction ? true : false)} onClick={endTurn}>End Turn</button>
                        <button onClick={() => tradeDialog.current.showModal()} >
                            Trade
                        </button>
                        <button className="start-auction" ref={auctionBtn} disabled={!!currentSpace?.owner || !currentSpace?.purchaseable || (auction ? true : false)} onClick={() => {
                            sendJsonMessage({ "action": "start-auction", "spaceid": currentSpace.id })
                        }}>Auction</button>
                    {jail?.owner === player.id &&
                        <input type="number" title="bail cost" className="bail" onChange={(e) => {
                            sendJsonMessage({"action": "set-bail", spaceid: jail.id, amount: Number(e.target.value)})
                        }} placeholder="bail cost" />}
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
