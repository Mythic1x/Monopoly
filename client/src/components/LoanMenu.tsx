import { Loan, Player } from "../../index";
import { FormEvent, useContext, useState } from "react";
import PlayerCard from "./PlayerCard";
import useWebSocket from "react-use-websocket/dist";
import ConnectionContext from "../../src/Contexts/ConnectionContext";
import SimplePlayerCard from "./SimplePlayerCard";

interface Props {
    players: Player[]
    currentPlayer: Player
    loanMenuClose: () => void
    loan?: Loan
}


function LoanMenu({ currentPlayer, players, loanMenuClose, loan }: Props) {
    const { ip } = useContext(ConnectionContext)
    const { sendJsonMessage } = useWebSocket(ip, {
        share: true
    })
    const [loanAmount, setLoanAmount] = useState(0)
    const [selectedPlayer, setSelectedPlayer] = useState<Player>(null)
    const [interestRate, setInterestRate] = useState(0.0)
    const [interestType, setInterestType] = useState<"simple" | "compound" | null>(null)
    const [loanType, setLoanType] = useState<"per-turn" | "deadline">("per-turn")
    const [amountPerTurn, setAmountPerTurn] = useState<number | null>(null)
    const [deadline, setDeadline] = useState<number | null>(null)
    const [bank, setBank] = useState(false)
    const maxAmount = bank ? currentPlayer.creditScore * 2.5 : Infinity
    
    function handleSubmit(e: FormEvent) {
        e.preventDefault()
        loanMenuClose()
        const loan: Loan = {
            loaner: bank ? null : selectedPlayer.id,
            amount: loanAmount,
            loanee: currentPlayer.id,
            interest: interestRate,
            interestType: interestType,
            type: loanType,
            amountPerTurn: amountPerTurn,
            deadline: deadline,
            status: "proposed"
        }

        sendJsonMessage({ "action": "loan", loan: loan })
    }

    function isFormInvalid() {
        return !loanAmount || (!selectedPlayer && !bank) || !interestRate || !interestType || !loanType || ((!amountPerTurn && loanType === "per-turn") || ((!deadline && loanType === "deadline") && !bank))
    }

    if (loan) {
        
        return (
            <dialog className="loan-menu-container m-0">
                <button className="delete" onClick={() => {
                    loanMenuClose()
                }}>X</button>
                <span className="player-name">{`${players.find(p => p.id === loan.loaner)?.name ?? "Bank"} to ${players.find(p => p.id === loan.loanee).name}`}</span>
                <span className="amount">{`Amount: $${loan.amount}`}</span>
                <div className="loan-grid-container">
                    <span className="interest">Interest</span>
                    <span className="interest-type">Interest Type</span>
                    <span className="condition">{loan.deadline ? "Deadline" : "Amount per turn"}</span>

                    <span className="interest">{loan.interest}%</span>
                    <span className="interest-type">{loan.interestType}</span>
                    <span className="condition">{loan.deadline ? `${loan.deadline} turns` : `$${loan.amountPerTurn}`}</span>
                </div>
                {(loan.loaner === currentPlayer.id && loan.status === "proposed") && <div className="action-buttons">
                    <button className="accept-button" onClick={() => {
                        sendJsonMessage({ "action": "accept-loan", "loan": loan.id })
                        loanMenuClose()
                    }}>Accept Loan</button>
                    <button className="decline-button" onClick={() => {
                        sendJsonMessage({ "action": "decline-loan", "loan": loan.id })
                        loanMenuClose()
                    }}>Decline Loan</button>
                </div>
                }
            </dialog>
        )
    }

    return (
        <>
            <dialog className="loan-menu-container m-0">
                <button className="close" onClick={() => loanMenuClose()}>X</button>
                {!bank && <><span className="selected-player">{selectedPlayer ? selectedPlayer.name : ""}</span>
                    <div className="players">{players.filter(p => p.id !== currentPlayer.id).map(player => {
                        return (
                            <button className={`list-player ${player.id === selectedPlayer?.id && "selected"}`} key={player.id} onClick={function (e) {
                                if (player.id === selectedPlayer?.id) {
                                    setSelectedPlayer(null);
                                } else {
                                    setSelectedPlayer(player);
                                }
                            }}>
                                <SimplePlayerCard player={player} />
                            </button>
                        )
                    })}
                    </div>
                    <hr />
                </>
                }
                <form onSubmit={handleSubmit}>
                    <div className="loan-options">
                        <div className="checkbox-group">
                            <input type="checkbox" name="bank" id="bank" onChange={e => {
                                setBank(e.target.checked)
                                setSelectedPlayer(null)
                            }} />
                            <label htmlFor="bank">Get Loan From Bank</label>
                        </div>
                        <label htmlFor="amount">{bank ? `Loan Amount (max amount $${maxAmount} based on credit score)` : "Loan amount"}</label>
                        <input type="number" placeholder="Loan Amount" id="amount" required value={loanAmount} onChange={e => {
                            const num = Number(e.target.value)
                            if (!isNaN(num) && num <= maxAmount) {
                                setLoanAmount(num)
                            }
                        }} />
                        <label htmlFor="interest">Interest Rate%</label>
                        <input type="number" placeholder="Interest Rate" id="interest" required value={interestRate} onChange={e => {
                            setInterestRate(Number(e.target.value))
                        }} />
                        <span className="interest-type">Interest Type</span>
                        <div className="checkbox-group">
                            <input type="radio" name="itype" id="simple" required onChange={e => {
                                if (e.target.checked) setInterestType("simple")
                            }} />
                            <label htmlFor="simple">Simple</label>
                            <input type="radio" name="itype" id="compound" onChange={e => {
                                if (e.target.checked) setInterestType("compound")
                            }} />
                            <label htmlFor="compound">Compound</label>
                        </div>
                        <select name="Loan Type" id="loan-type" className="loantype" required onChange={e => {
                            switch (e.target.value) {
                                case "per-turn":
                                    setLoanType(e.target.value)
                                    setDeadline(null)
                                    break
                                case "deadline":
                                    setLoanType(e.target.value)
                                    setAmountPerTurn(null)
                                    break
                            }
                        }}>
                            <option value="per-turn">Per Turn</option>
                            <option value="deadline">Deadline</option>
                        </select>

                        {loanType === "per-turn" && <input type="number" value={amountPerTurn ?? ""} placeholder="Amount Per Turn" required onChange={e => {
                            setAmountPerTurn(Number(e.target.value))
                        }} />}
                        {(loanType === "deadline" && !bank) && <input type="number" value={deadline ?? ""} placeholder="Deadline" required onChange={e => {
                            setDeadline(Number(e.target.value))
                        }} />}
                        <button type="submit" disabled={isFormInvalid()} className="submit-button">Send Loan</button>
                    </div>
                </form>
            </dialog>
        </>
    )
}

export default LoanMenu
