import useWebSocket from "react-use-websocket/dist";
import { Player, Space } from "../../index";
import { socketAddr } from "../../socket";

export default function SpaceCard({ space, player }: { space: Space, player: Player }) {
    const { sendJsonMessage } = useWebSocket(socketAddr, {
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
            console.log(space.houses, playerSpace.houses)
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
    return (
        <div className="space-card" data-anchor-name={`--space-${space.id}`}>
            <div className="space-card-name">{space.name}</div>
            <span className="owner">{space.owner ?? "Unowned"}</span>
            <div className="house-info">
                <div className="house-count">{space.houses} 🏠</div>
                <div className="hotel">{space.hotel ? 1 : 0} 🏨</div>
            </div>
            <div className="house-buttons-container">
                <button className="buy-house" disabled={!canBuyHouse()} onClick={() => {
                    sendJsonMessage({ "action": "buy-house", "spaceid": space.id })
                }}>Buy House</button>
                <button className="buy-hotel" disabled={!canBuyHotel()} onClick={() => {
                    sendJsonMessage({ "action": "buy-hotel", "spaceid": space.id })
                }}>Buy Hotel</button>
            </div>
        </div>
    )
}
