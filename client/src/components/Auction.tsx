import { SendJsonMessage } from "react-use-websocket/dist/lib/types";
import { Player, Space, Auction } from "../../index";
import { useContext, useEffect, useState } from "react";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

//time in ms
export default function AuctionMenu({ space, time, auction, sendJsonMessage }: { space: Space, time: number, auction: Auction, sendJsonMessage: SendJsonMessage }) {
    const { player, players } = useContext(MonopolyContext)
    let bidder: Player | undefined = players.find(p => p.id === auction.bidder)
    const [bidAmount, setBidAmount] = useState(null)
    const [bidTime, setBidTime] = useState(time)

    function sendBid(amount: number) {
        sendJsonMessage({ "action": "bid", "bid": amount })
    }

    function checkValidBid() {
        if (player.money < bidAmount) {
            return false
        }
        if (bidAmount < auction.current_bid) {
            return false
        }
        if(isNaN(bidAmount)) {
            return false
        }
        return true
    }

    useEffect(() => {
        const id = setInterval(() => setBidTime(t => t - 1))
        return () => clearInterval(id)
    }, [])
    return (
        <div className="auction-menu">
            <div className="auction-timer">
                <div className="timer-bar-container"><span className="time-bar" style={{ width: `${bidTime / 10}%` }}></span></div>
            </div>
            <div className="auction-status">
                <span className="bidder">{bidder?.name ?? "No bidder"}: </span>
                <span className="bid">${auction.current_bid.toString()}</span>
            </div>
            <div className="space-auctioned">
                <span className="space-name" style={{ color: space.attrs.color }}>{space.name}</span>
                <span className="space-cost">{space.cost}</span>
                <span className="house-cost">{space.attrs.house_cost}</span>
            </div>
            <input type="text" placeholder="enter your bid" onChange={(e) => setBidAmount(e.target.value)} />
            <button className="send-bid" disabled={!checkValidBid()} onClick={() => sendBid(bidAmount)}>Bid</button>
        </div>
    )
}