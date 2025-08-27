import useWebSocket from "react-use-websocket/dist";
import { Player, Space, Trade } from "../../index";
import { socketAddr } from "../../socket";
import PlayerCard from "./PlayerCard";
import { useContext, useState } from "react";
import { SendJsonMessage } from "react-use-websocket/dist/lib/types";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

interface Props {
    currentPlayer: Player
    players: Player[]
    tradeDialog: React.RefObject<HTMLDialogElement>
    currentTrade: Trade
    setCurrentTrade: React.Dispatch<React.SetStateAction<Trade>>
}

export default function TradeMenu({ currentPlayer, players, tradeDialog, currentTrade, setCurrentTrade }: Props) {
    const [selectedPlayer, setSelectedPlayer] = useState<Player>(null)
    const { sendJsonMessage } = useWebSocket(socketAddr, {
        share: true
    })

    function acceptTrade(trade: Trade) {
        sendJsonMessage({
            action: "accept-trade",
            trade: trade.trade,
            with: trade.with
        })
        setCurrentTrade(null)
    }

    function declineTrade() {
        setCurrentTrade(null)
    }

    if (currentTrade) {
        return (
            <dialog ref={tradeDialog} id="trade-dialog"><TradeProposal trade={currentTrade} proposingPlayer={players.find(p => p.id === currentTrade.with)} acceptTrade={acceptTrade} declineTrade={declineTrade}></TradeProposal></dialog>
        )
    }

    return (
        <dialog ref={tradeDialog} id="trade-dialog">
            <button className="delete-button" onClick={() => tradeDialog.current.close()}>X</button>
            <div className="trade-menu-players">
                <center><h3 className="trade-header">Trade</h3></center>
                {players.map((player) => (
                    <button className="trade-list-player" data-enable-shadow onClick={() => {
                        if (selectedPlayer === player) {
                            setSelectedPlayer(null)
                        } else {
                            setSelectedPlayer(player)
                        }
                    }} style={{ cursor: "pointer" }}>
                        <PlayerCard player={player}></PlayerCard>
                    </button>
                ))}</div>
            {selectedPlayer && <TradeSelection player={currentPlayer} otherPlayer={selectedPlayer} sendJsonMessage={sendJsonMessage} setSelectedPlayer={setSelectedPlayer}></TradeSelection>}
        </dialog>
    )
}

function TradeSelection({ player, otherPlayer, sendJsonMessage, setSelectedPlayer }: { player: Player, otherPlayer: Player, sendJsonMessage: SendJsonMessage, setSelectedPlayer: React.Dispatch<React.SetStateAction<Player>> }) {
    const [give, setGive] = useState<Space[]>([])
    const [receieve, setReceieve] = useState<Space[]>([])
    const [giveMoney, setGiveMoney] = useState(0)
    const [receieveMoney, setReceieveMoney] = useState(0)

    const canGive = player.ownedSpaces.filter((p: Space) => !give.some((g) => g.id === p.id))
    const canReceive = otherPlayer.ownedSpaces.filter((p: Space) => !receieve.some((r) => r.id === p.id))

    function sendTrade(trade: Trade) {
        sendJsonMessage({ action: "propose-trade", trade, playerid: trade.with })
        alert("trade sent")
        setSelectedPlayer(null)
    }

    return (
        <div className="trade-selection-menu">
            <div className="give-options">
                <h3 className="trade-selection-text">Properties</h3>
                {canGive.map((property) => (
                    <button className="space-give" onClick={() => {
                        setGive([...give, property])
                    }}>{property.name}</button>
                ))}
            </div>

            <div className="give-list">
                <h3 className="trade-selection-text">Give</h3>
                <input type="text" className="give-money" placeholder="$0" onChange={(e) => setGiveMoney(Number(e.target.value))} />
                {give.map((property) => (
                    <button className="space-give" onClick={() => {
                        const i = give.filter(prop => prop.id !== property.id)
                        setGive(i)
                    }}>{property.name}</button>
                ))}
            </div>

            <div className="receive-list">
                <h3 className="trade-selection-text">Get</h3>
                <input type="text" className="receieve-money" placeholder="$0" onChange={(e) => setReceieveMoney(Number(e.target.value))} />
                {receieve.map((property) => (
                    <button className="receive" onClick={() => {
                        const i = receieve.filter(prop => prop.id !== property.id)
                        setReceieve(i)
                    }}>{property.name}</button>
                ))}
            </div>

            <div className="receieve-options">
                <h3 className="trade-selection-text">{`${otherPlayer.name}'s Properties`}</h3>
                {canReceive.map((property) => (
                    <button className="receive" onClick={() => {
                        setReceieve([...receieve, property])
                    }}>{property.name}</button>
                ))}
            </div>

            <button className="send-trade" data-enable-shadow onClick={() => {
                const trade: Trade = {
                    trade: {
                        want: {
                            properties: [...receieve.map(property => Number(property.id))],
                            money: receieveMoney
                        },
                        give: {
                            properties: [...give.map(property => Number(property.id))],
                            money: giveMoney
                        },
                    },
                    with: otherPlayer.id
                }
                sendTrade(trade)
            }}>Send Trade</button>
        </div >
    )
}

function TradeProposal({
    trade,
    proposingPlayer,
    acceptTrade,
    declineTrade,
}: {
    trade: Trade
    proposingPlayer: Player
    acceptTrade: (trade: any) => void;
    declineTrade: () => void;
}) {

    const { board } = useContext(MonopolyContext)
    console.log(board)

    const propertiesToReceive = board.spaces.filter(space =>
        trade.trade.give.properties?.includes(Number(space.id))
    );
    const propertiesToGive = board.spaces.filter(space =>
        trade.trade.want.properties?.includes(Number(space.id))
    );

    const moneyToReceive = trade.trade.give.money;
    const moneyToGive = trade.trade.want.money;

    return (
        <div className="trade-proposal-menu">

            <center><h2 className="trade-proposal-title">
                Trade Proposal from {proposingPlayer.name}
            </h2>
            </center>
            <div className="give-list">
                <h3 className="trade-selection-text">You Give</h3>

                <div className="money-display">${moneyToGive}</div>

                {propertiesToGive.map((property) => (
                    <div key={property.id} className="space-display space-give">
                        {property.name}
                    </div>
                ))}
            </div>

            <div className="receive-list">
                <h3 className="trade-selection-text">You Get</h3>
                <div className="money-display">${moneyToReceive}</div>

                {propertiesToReceive.map((property) => (
                    <div key={property.id} className="space-display space-receive">
                        {property.name}
                    </div>
                ))}
            </div>

            <div className="trade-proposal-actions">
                <button className="accept-trade" data-enable-shadow onClick={acceptTrade}>
                    Accept
                </button>
                <button className="decline-trade" data-enable-shadow onClick={declineTrade}>
                    Decline
                </button>
            </div>
        </div>
    );
}
