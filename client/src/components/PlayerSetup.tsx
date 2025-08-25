import { useState, FormEvent } from "react";

function PlayerSetup({ onSetupComplete }: any) {
    const [name, setName] = useState('');
    const [piece, setPiece] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (!name || !piece) return;
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
            <button type="submit">Join Game</button>
        </form>
        </>
    );
}

export default PlayerSetup
