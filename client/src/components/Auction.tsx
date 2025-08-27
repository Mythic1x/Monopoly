import { SendJsonMessage } from "react-use-websocket/dist/lib/types";
import { Player, Space, Auction } from "../../index";
import { useContext, useEffect, useState } from "react";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

//time in ms
export default function AuctionMenu({ space, time, auction, sendJsonMessage }: { space: Space, time: number, auction: Auction, sendJsonMessage: SendJsonMessage }) {
    const { player, players } = useContext(MonopolyContext)
    const bidder: Player | undefined = players.find(p => p.id === auction.bidder)
    const [bidAmount, setBidAmount] = useState(null)
    const [timerWidth, setTimerWidth] = useState(100)

    function sendBid(amount: number) {
        sendJsonMessage({ "action": "bid", "bid": amount })
    }

    function checkValidBid() {
        if (player.money < bidAmount) {
            return false
        }
        if (bidAmount <= auction.current_bid) {
            return false
        }
        if (isNaN(bidAmount)) {
            return false
        }
        return true
    }
  
    useEffect(() => {
        const id = setInterval(() => setTimerWidth(t => t - 1), ((time) / 100))
        return () => {
            setTimerWidth(100)
            clearInterval(id)
        }
    }, [auction])
    return (
        <div className="auction-menu">
            <div className="auction-timer">
                <div className="timer-bar-container"><div className="time-bar" style={{ width: `${timerWidth}%` }}></div></div>
            </div>
            <div className="auction-status">
                <span className="bidder">{bidder?.name ?? "No bidder"}: </span>
                <span className="bid">${auction.current_bid.toString()}</span>
            </div>
            <div className="space-auctioned">
                <span className="space-name" style={{ color: space.attrs.color }}>{space.name}</span>
                <span className="space-cost">Value: {space.cost}</span>
                <span className="house-cost">House Cost: {space.attrs.house_cost}</span>
            </div>
            <input type="text" placeholder="enter your bid" value={bidAmount} onChange={(e) => setBidAmount(e.target.value)} />
            <button className="send-bid" disabled={!checkValidBid()} onClick={() => {
                sendBid(bidAmount)
                setBidAmount("")
                }}>Bid</button>
        </div>
    )
}