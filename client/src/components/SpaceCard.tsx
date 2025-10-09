import useWebSocket from "react-use-websocket/dist";
import { Player, Space } from "../../index";
import { useContext } from "react";
import ConnectionContext from "../../src/Contexts/ConnectionContext";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

export default function SpaceCard({ space, player }: { space: Space, player: Player }) {
    const {ip} = useContext(ConnectionContext)
    const { players } = useContext(MonopolyContext)
    const { sendJsonMessage } = useWebSocket(ip, {
        share: true
    })

    function canBuyHouse() {
        if (!player.sets.includes(space.attrs.color)) {
            return false
        } else if (player.money < space.attrs.house_cost) {
            return false
        } else if (space.houses === 4) {
            return false
        } else {
            const set = player.ownedSpaces.filter((s: Space) => s.attrs.color === space.attrs.color)
            for (const playerSpace of set) {
                if (space.houses > playerSpace.houses) {
                    return false
                }
            }
        }
        return true
    }

    function canBuyHotel() {
        if (space.owner !== player.id) {
            return false
        }
        if (space.houses < 4) {
            return false
        }
        const set = player.ownedSpaces.filter((s: Space) => s.attrs.color === space.attrs.color)
        for (const playerSpace of set) {
            if (playerSpace.houses < 4) {
                return false
            }
        }
        return true
    }

    function canSellHouse() {
        const set = player.ownedSpaces.filter((s: Space) => s.attrs.color === space.attrs.color)
        if(space.houses === 0) return false
        for (const playerSpace of set) {
            if (space.houses < playerSpace.houses || (space.hotel && !playerSpace.hotel)) {
                return false
            }
        }
        return true
    }

    function handleMortgage(unmortgage: boolean) {
        if (unmortgage) {
            sendJsonMessage({ "action": "unmortgage", "spaceid": space.id })
        } else {
            sendJsonMessage({ "action": "mortgage", "spaceid": space.id })
        }
    }

    return (
        <div className="space-card" data-anchor-name={`--space-${space.id}`}>
            <div className="space-card-name">{space.name}</div>
            <span className="owner">{players.find(p => p.id === space.owner)?.name ?? "Unowned"}</span>
            {space.name === "Jail" && <span className="bail-cost">Bail: ${space.attrs.bailcost}</span>}
            <div className="house-info">
                <div className="house-count">{space.houses} 🏠</div>
                <div className="hotel">{space.hotel ? 1 : 0} 🏨</div>
            </div>
            {space.owner === player.id &&
                <button className="mortgage-button" disabled={(space.mortgaged && player.money < space.cost * 0.10)} onClick={() => {
                    handleMortgage(space.mortgaged)
                }}>{space.mortgaged ? "Unmortgage" : "Mortgage"}</button>
            }
            {
                (space.attrs.house_cost && space.owner == player.id) &&
                <div className="house-buttons-container">
                    <div>
                        <span className="house-cost">{space.attrs.house_cost ?? ""}</span>
                        <button className="buy-house" disabled={!canBuyHouse()} onClick={() => {
                            sendJsonMessage({ "action": "buy-house", "spaceid": space.id })
                        }}>Buy House</button>
                    </div>
                    <div>
                        <span className="space-cost">{space.cost ?? ""}</span>
                        <button className="buy-hotel" disabled={!canBuyHotel()} onClick={() => {
                            sendJsonMessage({ "action": "buy-hotel", "spaceid": space.id })
                        }}>Buy Hotel</button>
                    </div>
                    <div>
                        <button className="sell-house" disabled={!canSellHouse()} onClick={() => {
                            sendJsonMessage({"action": "sell-house", "spaceid": space.id})
                        }}>Sell House</button>
                    </div>
                </div>
            }
        </div >
    )
}
