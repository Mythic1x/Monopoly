import { useContext, useState } from "react"
import { Loan } from "../../index"
import useWebSocket from "react-use-websocket/dist"
import MonopolyContext from "../../src/Contexts/MonopolyContext"
import ConnectionContext from "../../src/Contexts/ConnectionContext"

interface Props {
    loan: Loan
    loanPMenuClose: () => void
}

function LoanPaymentMenu({ loan, loanPMenuClose }: Props) {
    const { ip } = useContext(ConnectionContext)
    const { player } = useContext(MonopolyContext)
    const { sendJsonMessage } = useWebSocket(ip, {
        share: true
    })

    const [amount, setAmount] = useState(0)

    function payLoan() {
        sendJsonMessage({ "action": "pay-loan", "loan": loan.id, "amount": amount })
        loanPMenuClose()
    }

    return (
        <dialog className="loan-payment-menu m-0">
            <button className="close" onClick={() => {
                loanPMenuClose()
            }}>X</button>
            <div className="loan-info-container">
                <div className="loan-info">
                    <span className="interest">Interest: 
                        <span className="interest"> {loan.interest}%</span>
                    </span>

                    <span className="interest-type">Interest Type:
                        <span className="interest-type"> {loan.interestType}</span>
                    </span>

                    <span className="amount-due">Amount due:
                        <span className="amount-due"> {loan.remainingToPay}</span>
                    </span>

                    <span className="condition">{loan.deadline ? "deadline: " : "Amount per turn: "}
                        <span className="condition">{loan.deadline ? `In ${loan.deadline - loan.turnsPassed} turns` : loan.amountPerTurn}</span>
                    </span>
                </div>
            </div>

            {loan.deadline && (
                <>
                    <input type="number" value={amount} onChange={(e) => {
                        const num = Number(e.target.value)
                        if (amount + num <= loan.remainingToPay) setAmount(num)
                    }} />
                    <button className="pay-loan" onClick={payLoan}>Pay Amount</button>
                </>
            )}
        </dialog>
    )
}

export default LoanPaymentMenu
