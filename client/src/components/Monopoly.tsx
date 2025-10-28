import { useState, useEffect, useRef, useContext } from "react"
import { Board, Space, Player, ServerResponse, Trade, Auction, playerid_t, spaceid_t, Loan } from "../../index"
import PlayerCard from "./PlayerCard"
import useWebSocket, { ReadyState } from "react-use-websocket/dist"
import usePlayer from "../hooks/useplayer"
import GameBoard from "./board"
import Alert from "./alert"
import TradeMenu from "./TradeMenu"
import MonopolyContext, { MonopolyProvider } from "../../src/Contexts/MonopolyContext"
import AuctionMenu from "./Auction"
import ConnectionContext from "../../src/Contexts/ConnectionContext"
import LoanMenu from "./LoanMenu"

function Monopoly({ playerDetails }: any) {
    const [alertQ, setAQ] = useState<string[]>([])

    const rollBtn = useRef<HTMLButtonElement>(null)
    const buyBtn = useRef<HTMLButtonElement>(null)
    const auctionBtn = useRef<HTMLButtonElement>(null)

    const tradeDialog = useRef<HTMLDialogElement>(null)

    const [currentTrade, setCurrentTrade] = useState<Trade | null>(null)
    const [auction, setAuction] = useState<Auction | null>(null)

    const { ip } = useContext(ConnectionContext)
    const { board, player, players, setBoard, setPlayers, playerLoaded, setPlayer } = useContext(MonopolyContext)
    const activePlayers = players.filter(p => !p.bankrupt)

    function playerById(id: playerid_t) {
        return activePlayers.find(v => v.id === id)
    }

    function spaceById(id: spaceid_t) {
        return board.spaces.find(v => v.id === id)
    }

    const [rolled, setRolled] = useState<boolean>(false)
    const [loading, setLoading] = useState(true)
    const [currentSpace, setCurrentSpace] = useState<Space | null>(null)
    const [goingPlayer, setGoingPlayer] = useState<Player | null>(null)
    const [showLoanMenu, setShowLoanMenu] = useState(false)
    const [trades, setTrades] = useState<Trade[]>([])
    const [loans, setLoans] = useState<Loan[]>([])
    const [loan, setLoan] = useState(null)
    

    const { sendJsonMessage, lastJsonMessage, readyState, } = useWebSocket(ip, {
        share: true
    })

    function handleStatus(status: any) {
        switch (status.status) {
            case "due-loan":
                return `${playerById(status.player).name} has a loan due: ${status.loan.id}`
            case "accepted-loan":
                return `${playerById(status.loanee.id).name} has been given a loan from ${playerById(status.loaner.id)?.name ?? "the bank"}`
            case "bankrupt":
                return `${playerById(status.player).name} has gone bankrupt`
            case "draw-chance":
                return status.event
            case "fail":
                return `${playerById(status.player).name} has failed`
            case "mortgage-success":
                return `${playerById(status.player).name} has mortgaged ${spaceById(status.space).name}`
            case "unmortgage-success":
                return `${playerById(status.player).name} has unmortgaged ${spaceById(status.space).name}`
            case "buy-fail":
                return `Failed to buy`
            case "buy-house-fail":
                return "Failed to buy communist 🏘️"
            case "buy-hotel-fail":
                return "you バカ, you could not buy a hotel"
            case "buy-success":
                return "(russian accent) bought 😏"
            case "buy-house-success":
                return "HOUSING"
            case "buy-hotel-success":
                return "HOTELING"
            case "buy-new-set":
                return `The ftc is watching as ${spaceById(status.space).attrs.color} has become a monopoly`
            case "prompt-to-buy":
                return `${spaceById(status.space).name} is available for purchase`
            case "money-lost":
                return `${status.amount} has been lost`
            case "money-given":
                return `${status.amount} was given`
            case "auction-end":
                return `${spaceById(status.space).name} has been auctioned`
            case "none":
                return ""
            case "pay-other":
                return `${playerById(status.player).name} is paying ${playerById(status.other).name} $${status.amount}`
            case "pay-tax":
                return `${status.amount} has been paid for ${status.taxname} tax`
            case "pass-go":
                return 'go has been passed, very nifty'
            case 'pay-jail':
                return `${status.cost} has been paid in bail`
        }
    }

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

    function loanMenuClose() {
        setShowLoanMenu(false)
        if (loan) setLoan(null)
      
    }

    useEffect(() => {
        const id = setInterval(() => {
            if (alertQ.length > 0) {
                setAQ(q => q.slice(1))
            }
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
                case "trade-list":
                    setTrades(message.value)
                    break
                case "loan-list":
                    setLoans(message.value)
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
                    let m = handleStatus(message.value)
                    if (m) alert(m)
                    break
                case "join-game":
                    sendJsonMessage({ 'action': "connect" })
                    sendJsonMessage({ 'action': "current-space" })
                    break
                case "trade-proposal":
                    setCurrentTrade(message.value)
                    tradeDialog.current.showModal()
                    break
                case "loan-proposal":
                    setLoan(message.value)
                    setShowLoanMenu(true)
                    break
                case "auction-status":
                    setAuction(message.value)
                    break
                case "auction-end":
                    setAuction(null)
                    break
                case "bankrupt":
                    alert(`${message.value} went bankrupt!`)
                    break
                case "game-end":
                    alert(`${message.value.name} won!`)
                    break
            }
        }
    }, [lastJsonMessage])


    if (loading || !playerLoaded) {
        return <span className="loading">loading...</span>
    }

    let jail = board.spaces.find(v => v.name === "Jail")
    return <>
        <TradeMenu currentPlayer={player} players={activePlayers} tradeDialog={tradeDialog} currentTrade={currentTrade} setCurrentTrade={setCurrentTrade}></TradeMenu>
        {showLoanMenu && <LoanMenu currentPlayer={player} players={players} loanMenuClose={loanMenuClose} loan={loan}></LoanMenu>}
        <div id="game">
            <div className="board-container">
                <GameBoard board={board} player={player}>
                    {auction &&
                        <AuctionMenu space={board.spaces.find(s => s.id === auction.space)} time={auction.end_time} auction={auction} sendJsonMessage={sendJsonMessage}></AuctionMenu>
                    }
                    <div id="alert-container">
                        {alertQ.map(v => <Alert alert={v} />)}
                    </div>
                    {!player.bankrupt && <div className="button-container">
                        <div className="action-buttons">
                            <button ref={rollBtn} className="roll" disabled={goingPlayer?.id !== player.id || rolled || (auction ? true : false) || player.bankrupt} onClick={() => {
                                sendJsonMessage({ "action": "roll" })
                            }}>Roll</button>
                            {(goingPlayer?.id === player.id) && <button ref={buyBtn} className="buy" disabled={!!currentSpace?.owner || !currentSpace?.purchaseable || player.money < currentSpace.cost || player.bankrupt || !!auction} onClick={() => {
                                sendJsonMessage({ "action": "buy", "spaceid": currentSpace.id })
                            }}>Buy Property</button>
                            }
                            <button className="end-turn" disabled={goingPlayer?.id !== player.id || !rolled || (auction ? true : false) || player.bankrupt || player.money < 0} onClick={endTurn}>End Turn</button>
                            <button onClick={() => setShowLoanMenu(!showLoanMenu)} disabled={player.bankrupt} id="loan-button">Loan</button>
                            <button onClick={() => tradeDialog.current.showModal()} disabled={player.bankrupt} >
                                Trade
                            </button>
                            <button className="start-auction" ref={auctionBtn} disabled={!!currentSpace?.owner || !currentSpace?.purchaseable || (auction ? true : false) || player.bankrupt || goingPlayer?.id !== player.id} onClick={() => {
                                sendJsonMessage({ "action": "start-auction", "spaceid": currentSpace.id })
                            }}>Auction</button>
                            {player.money >= jail.attrs.bailcost && player.injail && !rolled && <button className="pay-bail" onClick={() => sendJsonMessage({ "action": "pay-bail" })}>
                                Pay bail
                            </button>}
                            {jail?.owner === player.id &&
                                <input type="number" title="bail cost" className="bail" onChange={(e) => {
                                    sendJsonMessage({ "action": "set-bail", spaceid: jail.id, amount: Number(e.target.value) })
                                }} placeholder="bail cost" />}
                        </div>
                        <button className="bankrupt" disabled={player.bankrupt || !!auction} style={{ background: "red" }} onClick={() => {
                            sendJsonMessage({ "action": "bankrupt" })
                        }}>Bankrupt</button>
                    </div>
                    }
                </GameBoard>

            </div>
            <div className="player-list">
                <h3>Players</h3>
                {players?.map((player) => (
                    <PlayerCard player={player} key={player.id}></PlayerCard>
                ))}
            </div>
            <div className="trade-loan-grid">
                <div className="trades-column">
                <h3>Trades</h3>
                {trades?.map(trade => (
                    <div className="trade-list-item" onClick={() => {
                        setCurrentTrade(trade)
                        tradeDialog?.current.showModal()
                    }}>
                        <span className="sender">{playerById(trade.sender).name}</span>
                        <span className="recipient">{playerById(trade.recipient).name}</span>
                    </div>
                ))}
                </div>

                <div className="loans-column">
                <h3>Loans</h3>
                {loans?.map(loan => (
                    <div className="loan-list-item" onClick={() => {
                        setLoan(loan)
                        setShowLoanMenu(true)
                    }}>
                        <span className="sender">{playerById(loan.loaner).name}</span>
                        <span className="recipient">{playerById(loan.loanee).name}</span>
                    </div>
                ))}
                </div>
            </div>
        </div>
    </>
}

export default Monopoly
