import { createContext, ReactNode, useState } from "react";

interface ConnectionContext {
    ip: string
    setIp: React.Dispatch<React.SetStateAction<string>>
}

const ConnectionContext = createContext<ConnectionContext>(undefined)

export function ConnectionProvider({ children }: { children: ReactNode }) {
    const [ip, setIp] = useState((localStorage.getItem("cachedIp") ?? ''))

    const contextValue = {
        ip,
        setIp
    }

    return (
        <ConnectionContext value={contextValue}>
            {children}
        </ConnectionContext>
    )
}

export default ConnectionContext