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
        } else if (player.money < space.houseCost) {
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
    return (
        <div className="space-card">
            <div className="space-card-name">{space.name}</div>
            <span className="owner">{space.owner ?? "Unowned"}</span>
            <div className="house-list">
                <li className="houses">
                    <div className="house1">{`House 1 🏚, Owned: ${space.houses >= 1}`}</div>
                    <div className="house2">{`House 2 🏠, Owned: ${space.houses >= 2}`}</div>
                    <div className="house3">{`House 3 🏡, Owned: ${space.houses >= 3}`}</div>
                    <div className="house4">{`House 4 🏘, Owned: ${space.houses >= 4}`}</div>
                    <div className="hotel">{`Hotel 🏨, Owned: ${space.hotel}`}</div>
                </li>
                <div className="house-buttons-container">
                    <button className="buy-house" disabled={!canBuyHouse()} onClick={() => {
                        sendJsonMessage({ "action": "buy-house", "spaceid": space.id })
                    }}>Buy House</button>
                    <button className="buy-hotel" disabled={!canBuyHotel()} onClick={() => {
                        sendJsonMessage({ "action": "buy-hotel", "spaceid": space.id })
                    }}>Buy Hotel</button>
                </div>
            </div>
        </div>
    )
}
