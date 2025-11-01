import usePlayer from "../../src/hooks/useplayer";
import { Board, LobbyState, Player } from "../../index";
import { createContext, ReactNode, useState } from "react";

interface MonopolyContext {
    board: Board | null
    player: Player | null
    players: Player[]
    setBoard: React.Dispatch<React.SetStateAction<Board>>
    setPlayers: React.Dispatch<React.SetStateAction<Player[] | []>>
    playerLoaded: boolean
    setPlayer: React.Dispatch<React.SetStateAction<Player>>
    lobbyState: LobbyState
    setLobbyState: React.Dispatch<React.SetStateAction<LobbyState>>
}

const MonopolyContext = createContext<MonopolyContext>(undefined)

export function MonopolyProvider({ children }: { children: ReactNode }) {
    const [board, setBoard] = useState<Board | null>(null)
    const [players, setPlayers] = useState<Player[] | []>([])
    const [lobbyState, setLobbyState] = useState<LobbyState | null>(null)
    const { player, playerLoaded, setPlayer } = usePlayer()

    const contextValue = {
        board,
        player,
        players,
        setBoard,
        setPlayers,
        playerLoaded,
        setPlayer,
        lobbyState,
        setLobbyState
    };

    return (
        <MonopolyContext.Provider value={contextValue}>
            {children}
        </MonopolyContext.Provider>
    )
}

export default MonopolyContext