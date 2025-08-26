import { Player, ServerResponse } from "../../index";
import { useEffect, useState } from "react";
import useWebSocket from "react-use-websocket/dist";
import { socketAddr } from "../../socket";

export default function usePlayer() {
    const [player, setPlayer] = useState<Player | null>(null)
    const [playerLoaded, setPlayerLoaded] = useState(false)
    const { sendJsonMessage, lastJsonMessage, readyState, } = useWebSocket(socketAddr, {
        share: true
    })
    useEffect(() => {
        if (!player && !playerLoaded) {
            sendJsonMessage({ "action": "send-player-info" })
        }

    }, [readyState])

    useEffect(() => {
        const message = lastJsonMessage as ServerResponse
        if (!message) return
        if (Array.isArray(message)) {
            if (message[0].response === "player-info") {
                setPlayer(message[0].value)
                setPlayerLoaded(true)
            }
        } else {
            if (message.response === "player-info") {
                setPlayer(message.value)
                setPlayerLoaded(true)
            }
        }
    }, [lastJsonMessage])
    return { player, playerLoaded }
}