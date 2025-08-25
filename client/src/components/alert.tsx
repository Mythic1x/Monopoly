export default function Alert({ alert }: { alert: string }) {
    return <>
        <span className="alert">{alert}</span>
    </>
}