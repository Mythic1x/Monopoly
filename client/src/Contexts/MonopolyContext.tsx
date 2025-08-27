import usePlayer from "../../src/hooks/useplayer";
import { Board, Player } from "../../index";
import { createContext, ReactNode, useState } from "react";

interface MonopolyContext {
    board: Board | null
    player: Player | null
    players: Player[]
    setBoard: React.Dispatch<React.SetStateAction<Board>>
    setPlayers: React.Dispatch<React.SetStateAction<Player[] | []>>
    playerLoaded: boolean
    setPlayer: React.Dispatch<React.SetStateAction<Player>>
}

const MonopolyContext = createContext<MonopolyContext>(undefined)

export function MonopolyProvider({ children }: { children: ReactNode }) {
    const [board, setBoard] = useState<Board | null>(null)
    const [players, setPlayers] = useState<Player[] | []>([])
    const { player, playerLoaded, setPlayer } = usePlayer()

    const contextValue = {
        board,
        player,
        players,
        setBoard,
        setPlayers,
        playerLoaded,
        setPlayer
    };

    return (
        <MonopolyContext.Provider value={contextValue}>
            {children}
        </MonopolyContext.Provider>
    )
}

export default MonopolyContext