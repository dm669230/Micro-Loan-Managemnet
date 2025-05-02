import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

export default function Dashboard() {
  const navigate = useNavigate();
  const [loanData, setLoanData] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loanStatus, setLoanStatus] = useState("Pending");

  const approved = loanData.filter((loan) => loan.loan_status == "Approved");
  const pending = loanData.filter((loan) => loan.loan_status == "Pending");

  const columns = ["Name", "Email", "Loan amount", "Interest rate", "Start date", "End date"];
  const access_token = localStorage.getItem("access_token") || "";
  useEffect(() => {
    if (access_token) {
      try {
        const data = jwtDecode(access_token);
        setIsAdmin(data.is_admin);
      } catch (err) {
        console.error("Invalid token");
        navigate("/login");
      }

      axios
        .get("http://127.0.0.1:8000/manageloan/get_all_loans", {
          headers: { Authorization: "Bearer " + access_token },
        })
        .then((res) => {
          if (res.status == 200) setLoanData(res.data.data);
          else alert("Loan not found");
        })
        .catch((err) => {
          console.log(err);
        });
    } else {
      alert("Please login first");
      navigate("/login");
    }
  }, [navigate, loanStatus]);

  function handleAction(loan_id, loan_status) {
    axios
      .patch(
        `http://127.0.0.1:8000/manageloan/update/${loan_id}`,
        { loan_status },
        {
          headers: { Authorization: "Bearer " + access_token },
        }
      )
      .then((res) => {
        console.log(res.data);
        setLoanStatus(loan_status);
      })
      .catch((err) => {
        console.log(err);
      });
  }

  return (
    <div className="dashboard">
      <h2>{isAdmin ? "Admin " : "User "}Dashboard</h2>
      {loanData.length > 0 ? (
        <div>
          {isAdmin && approved.length > 0 && (
            <div>
              <h3>Approved applications</h3>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr>
                    {columns.map((col, idx) => (
                      <th key={"col" + idx} style={{ border: "1px solid black", padding: "8px" }}>
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {approved.map((loan, index) => (
                    <tr key={"loan" + index}>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.user_name}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.user_email}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.loan_amount}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.interest_rate}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.start_date}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>{loan.end_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {isAdmin && pending.length > 0 && (
            <div>
              <h3>Pending applications</h3>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr>
                    {columns.map((col, idx) => (
                      <th key={"col" + idx} style={{ border: "1px solid black", padding: "8px" }}>
                        {col}
                      </th>
                    ))}
                    <th style={{ border: "1px solid black", padding: "8px" }}>Approv/Reject</th>
                  </tr>
                </thead>
                <tbody>
                  {pending.map((loan, index) => (
                    <tr key={"loan" + index}>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.user_name}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.user_email}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.loan_amount}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.interest_rate}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.start_date}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>{loan.end_date}</td>
                      <td
                        style={{
                          border: "1px solid black",
                          padding: "8px",
                          display: "flex",
                          justifyContent: "space-evenly",
                        }}
                      >
                        <button
                          style={{ background: "red" }}
                          onClick={() => {
                            handleAction(loan.loan_id, "Rejected");
                          }}
                        >
                          Reject
                        </button>
                        <button
                          style={{ background: "green" }}
                          onClick={() => {
                            handleAction(loan.loan_id, "Approved");
                          }}
                        >
                          Approv
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!isAdmin && (
            <div>
              <h3>Your application</h3>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr>
                    {columns.map((col, idx) => (
                      <th key={"col" + idx} style={{ border: "1px solid black", padding: "8px" }}>
                        {col}
                      </th>
                    ))}
                    <th style={{ border: "1px solid black", padding: "8px" }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {loanData.map((loan, index) => (
                    <tr key={"loan" + index}>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.user_name}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.user_email}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.loan_amount}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.interest_rate}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.start_date}
                      </td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>{loan.end_date}</td>
                      <td style={{ border: "1px solid black", padding: "8px" }}>
                        {loan.loan_status}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <div>
          {isAdmin ? (
            <p>No applications</p>
          ) : (
            <button
              onClick={() => {
                navigate("/apply-loan");
              }}
            >
              Apply for loan
            </button>
          )}
        </div>
      )}
    </div>
  );
}
