import useWebSocket from "react-use-websocket/dist";
import { Player, Space, Trade } from "../../index";
import PlayerCard from "./PlayerCard";
import { useContext, useState } from "react";
import { SendJsonMessage } from "react-use-websocket/dist/lib/types";
import MonopolyContext from "../../src/Contexts/MonopolyContext";
import ConnectionContext from "../../src/Contexts/ConnectionContext";

interface Props {
    currentPlayer: Player
    players: Player[]
    tradeDialog: React.RefObject<HTMLDialogElement>
    currentTrade: Trade
    setCurrentTrade: React.Dispatch<React.SetStateAction<Trade>>
}

export default function TradeMenu({ currentPlayer, players, tradeDialog, currentTrade, setCurrentTrade }: Props) {
    const [selectedPlayer, setSelectedPlayer] = useState<Player>(null)
    const { ip } = useContext(ConnectionContext)
    const { sendJsonMessage } = useWebSocket(ip, {
        share: true
    })

    function acceptTrade(trade: Trade) {
        sendJsonMessage({
            action: "accept-trade",
            id: trade.id,
            trade: trade.trade,
            recipient: trade.recipient,
            sender: trade.sender
        })
        setCurrentTrade(null)
    }

    function declineTrade(trade: Trade) {
        sendJsonMessage({ action: "decline-trade", id: trade.id })
        setCurrentTrade(null)
    }

    if (currentTrade) {
        return (
            <dialog ref={tradeDialog} id="trade-dialog"><TradeProposal trade={currentTrade} tradeDialog={tradeDialog} proposingPlayer={players.find(p => p.id === currentTrade.recipient)} acceptTrade={acceptTrade} declineTrade={declineTrade}></TradeProposal></dialog>
        )
    }

    return (
        <dialog ref={tradeDialog} id="trade-dialog">
            <button className="close" onClick={() => tradeDialog.current.close()}>X</button>
            <div className="players">
                <center><h3 className="trade-header">Trade</h3></center>
                {players.map((player) => (
                    <button className="list-player" key={player.id} data-enable-shadow onClick={() => {
                        if (selectedPlayer === player) {
                            setSelectedPlayer(null)
                        } else {
                            setSelectedPlayer(player)
                        }
                    }} style={{ cursor: "pointer" }}>
                        <PlayerCard player={player} goingPlayer={undefined}></PlayerCard>
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
        sendJsonMessage({ action: "propose-trade", trade: trade.trade, playerid: trade.recipient, sender: player.id })
        setSelectedPlayer(null)
    }

    return (
        <div className="trade-selection-menu">
            <div className="give-options">
                <h3 className="trade-selection-text">Properties</h3>
                {canGive.map((property) => (
                    <button className="space-give" key={property.id} onClick={() => {
                        setGive([...give, property])
                    }}>{property.name}</button>
                ))}
            </div>

            <div className="give-list">
                <h3 className="trade-selection-text">Give</h3>
                <input type="text" className="give-money" placeholder="$0" onChange={(e) => setGiveMoney(Number(e.target.value))} />
                {give.map((property) => (
                    <button className="space-give" key={property.id} onClick={() => {
                        const i = give.filter(prop => prop.id !== property.id)
                        setGive(i)
                    }}>{property.name}</button>
                ))}
            </div>

            <div className="receive-list">
                <h3 className="trade-selection-text">Get</h3>
                <input type="text" className="receieve-money" placeholder="$0" onChange={(e) => setReceieveMoney(Number(e.target.value))} />
                {receieve.map((property) => (
                    <button className="receive" key={property.id} onClick={() => {
                        const i = receieve.filter(prop => prop.id !== property.id)
                        setReceieve(i)
                    }}>{property.name}</button>
                ))}
            </div>

            <div className="receieve-options">
                <h3 className="trade-selection-text">{`${otherPlayer.name}'s Properties`}</h3>
                {canReceive.map((property) => (
                    <button className="receive" key={property.id} onClick={() => {
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
                    recipient: otherPlayer.id,
                    sender: player.id,
                    status: "proposed"
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
    tradeDialog,
}: {
    trade: Trade
    proposingPlayer: Player
    acceptTrade: (trade: Trade) => void;
    declineTrade: (trade: Trade) => void;
    tradeDialog: React.RefObject<HTMLDialogElement>
}) {

    const { board, player } = useContext(MonopolyContext)

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
                <div className="delete" onClick={() => {
                    tradeDialog.current?.close()
                }}>X</div>
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

            {(player.id === trade.recipient && trade.status === "proposed") && <div className="trade-proposal-actions">
                <button className="accept-trade" data-enable-shadow onClick={() => acceptTrade(trade)}>
                    Accept
                </button>
                <button className="decline-trade" data-enable-shadow onClick={() => {
                    tradeDialog.current?.close()
                    declineTrade(trade)
                }}>
                    Decline
                </button>
            </div>}
        </div>
    );
}
