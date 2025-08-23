import { useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

function App() {
    const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket("ws://localhost:8765", {share: true})
    useEffect(() => {
        console.log(lastJsonMessage)
    }, [lastJsonMessage, sendJsonMessage])

    return <>
        <div className="hi">Hi</div>
    </>
}

export default App