import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import axios from "axios";

export default function LoanApplication() {
  const navigate = useNavigate();
  const [loanData, setLoanData] = useState({
    loan_amount: "",
    interest_rate: "",
    start_date: "",
    end_date: "",
  });

  const access_token = localStorage.getItem("access_token") || "";
  useEffect(() => {
    if (!access_token) {
      alert("Please login first");
      navigate("/login");
      return;
    }
    try {
      const data = jwtDecode(access_token);
      if (data.is_admin) {
        alert("Admins can't apply for a loan");
        navigate("/dashboard");
      }
    } catch (err) {
      console.error("Invalid token", err);
      navigate("/login");
    }
  }, []);

  function isInputValid() {
    if (Number(loanData.loan_amount) < 10000) {
      alert("Loan amount can not be less than 10000");
      return false;
    }
    if (Number(loanData.interest_rate) < 7 || Number(loanData.interest_rate) > 15) {
      alert("Interest rate can only be within 7 to 15 percent");
      return false;
    }
    const today = new Date().toISOString().slice(0, 10);
    const start = new Date(loanData.start_date).toISOString().slice(0, 10);
    const end = new Date(loanData.end_date).toISOString().slice(0, 10);
    if (start < today) {
      alert("Start date can not be in past");
      return false;
    }
    if (end <= start) {
      alert("End date nust be more than start date");
      return false;
    }
    return true;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (isInputValid())
      console.log(loanData)
      axios
        .post("http://127.0.0.1:8000/manageloan/loan_application", loanData, {
          headers: { Authorization: "Bearer " + access_token },
        })
        .then((res) => {
          alert("Successfully applied for loan!");
          navigate("/dashboard");
        })
        .catch((err) => {
          alert("Loan application failed");
        });
  };

  return (
    <div className="loadn-application">
      <div></div>
      <div>
        <h2>Apply for Loan</h2>
        <form onSubmit={handleSubmit}>
          <input
            required
            type="number"
            placeholder="Loan Amount"
            onChange={(e) => setLoanData((prev) => ({ ...prev, loan_amount: e.target.value }))}
          />
          <input
            required
            type="number"
            placeholder="Interest Rate"
            onChange={(e) => setLoanData((prev) => ({ ...prev, interest_rate: e.target.value }))}
          />
          <input
            required
            type="date"
            placeholder="Start Date"
            onChange={(e) => setLoanData((prev) => ({ ...prev, start_date: e.target.value }))}
          />
          <input
            required
            type="date"
            placeholder="End Date"
            onChange={(e) => setLoanData((prev) => ({ ...prev, end_date: e.target.value }))}
          />
          <button onClick={handleSubmit} type="submit">
            Apply
          </button>
        </form>
      </div>
    </div>
  );
}
