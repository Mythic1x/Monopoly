import useWebSocket from "react-use-websocket/dist";
import { Player, Trade } from "../../index";
import { socketAddr } from "../../socket";

interface Props {
    players: Player[]
    tradeDialog: React.RefObject<HTMLDialogElement>
    currentTrade: Trade
}

export default function TradeMenu({ players, tradeDialog, currentTrade }: Props) {
    const { sendJsonMessage } = useWebSocket(socketAddr, {
        share: true
    })

    function acceptTrade(trade: Trade) {
        sendJsonMessage({
            action: "accept-trade",
            trade: trade.trade,
            with: trade.with
        })
    }
    return (
        <dialog ref={tradeDialog} id="trade-dialog">
            <button onClick={() => tradeDialog.current.close()} className="close-button">X</button>
            <div className="want">
                <h4>Want</h4>
                <p>&lt;- ${currentTrade?.trade.want.money || 0}</p>
            </div>
            <div className="give">
                <h4>Give</h4>
                <p>-&gt; ${currentTrade?.trade.give.money}</p>
            </div>
            <div className="trade-button-container">
                <button onClick={() => acceptTrade(currentTrade)}>
                    Accept Trade
                </button>
            </div>
        </dialog>
    )
}