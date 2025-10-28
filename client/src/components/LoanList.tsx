import { useContext } from "react";
import { Player, Loan } from "../../index";
import MonopolyContext from "../../src/Contexts/MonopolyContext";

interface Props {
    player: Player
    loanPMenuOpen: (loan: Loan) => void
    setShowLoanListMenu: React.Dispatch<React.SetStateAction<boolean>>

}

function LoanList({ player, loanPMenuOpen, setShowLoanListMenu }: Props) {
    const {players} = useContext(MonopolyContext)
    return (
        <dialog className="loans-list m-0">
            <button className="close" onClick={() => {
                setShowLoanListMenu(false)
            }}>X</button>
            {player.loans.map(loan => (
                <button className="loan-card" onClick={() => {
                    loanPMenuOpen(loan)
                }}>
                    <span className="loaner">{`From: ${players.find(p => p.id === loan.loaner)?.name}`}</span>
                    <span className="amount">${loan.amount}</span>
                </button>
            ))}
        </dialog>
    )
}

export default LoanList
