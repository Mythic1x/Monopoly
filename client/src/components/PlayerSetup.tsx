import { useState, FormEvent, useContext, useRef } from "react";
import MonopolyContext from "../../src/Contexts/MonopolyContext";
import ConnectionContext from "../../src/Contexts/ConnectionContext";

function PlayerSetup({ onSetupComplete }: any) {
    const [name, setName] = useState('');
    const [piece, setPiece] = useState('');
    const { ip, setIp } = useContext(ConnectionContext)

    setIp("0.0.0.0")
    const ipIn = useRef<HTMLInputElement>(null)

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        setIp(ipIn.current.value)
        if (!name || !piece) return;
        setIp(`http://${ip}:8765`)
        localStorage.setItem('cachedIp', ip);
        onSetupComplete({ name, piece });
    };

    return (<>
        <center><h1>Fucking Login screen</h1><p>
            Not fucking ai generated, get out with your ai generated login screens.
        </p></center>
        <form onSubmit={handleSubmit} className="selection-box">
            <input
                type="text"
                className="name-input"
                placeholder='Enter your name'
                value={name}
                onChange={(e) => setName(e.target.value)}
            />
            <input
                type="text"
                className="piece-selection"
                placeholder='Enter your piece'
                value={piece}
                onChange={(e) => setPiece(e.target.value)}
            />
            <input type="text" className="ip-selection" placeholder="0.0.0.0" ref={ipIn} />
            <button type="submit">Join Game</button>
        </form>
    </>
    );
}
export default PlayerSetup
