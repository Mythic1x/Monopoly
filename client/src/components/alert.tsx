import { useState } from "react"

export default function Alert({ alert }: { alert: string }) {
    let [hidden, setHidden] = useState(false)
    return <>
        {hidden ||
            <div className="alert" onClick={setHidden.bind(this, !hidden)}>{alert}</div>
        }
    </>
}
