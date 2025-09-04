import { createRoot } from 'react-dom/client'
import App from './main'
import { ConnectionProvider } from './Contexts/ConnectionContext'

const root = createRoot(document.body)

root.render(
    <ConnectionProvider>
        <App />
    </ConnectionProvider>
)
