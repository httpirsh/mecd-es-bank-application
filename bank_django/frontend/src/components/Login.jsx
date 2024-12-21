import React, { useState } from "react";

const LoanApplication = () => {
  const [step, setStep] = useState("login"); // Tracks the current step: "login" or "application"
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");
  const [monthlyIncome, setMonthlyIncome] = useState("");
  const [monthlyExpenses, setMonthlyExpenses] = useState("");
  const [loanResult, setLoanResult] = useState(null);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    if (!image) {
      setMessage("Please upload an image.");
      return;
    }

    const formData = new FormData();
    formData.append("image", image);

    try {
      // Authenticate via facial recognition
      const response = await fetch("http://127.0.0.1:8000/api/login/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Login failed.");
      }

      const data = await response.json();
      localStorage.setItem("token", data.token); // Save JWT token
      setMessage("Login successful! Please fill in your financial details.");
      setStep("application"); // Move to the loan application step
    } catch (err) {
      setMessage(err.message);
    }
  };

  const handleLoanSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    const token = localStorage.getItem("token");
    if (!token) {
      setMessage("You must be logged in to submit your loan application.");
      return;
    }

    // Retrieve saved loan configuration
    const loanConfiguration = JSON.parse(localStorage.getItem("loan_configuration"));

    if (!loanConfiguration) {
      setMessage("No loan configuration found. Please simulate a loan first.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/loan-application/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          monthly_income: parseFloat(monthlyIncome),
          monthly_expenses: parseFloat(monthlyExpenses),
          loan_amount: loanConfiguration.loan_amount,
          loan_duration: loanConfiguration.loan_duration,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Loan application failed.");
      }

      const data = await response.json();
      setLoanResult(data); // Display loan application result
      setMessage("Loan application submitted successfully!");
    } catch (err) {
      setMessage(err.message);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "2rem" }}>
      {step === "login" && (
        <div>
          <h1>Login</h1>
          <form onSubmit={handleLoginSubmit}>
            <label>Upload Image:</label>
            <input type="file" onChange={handleImageChange} />
            <button type="submit">Login</button>
          </form>
          {message && <p style={{ color: "blue", marginTop: "1rem" }}>{message}</p>}
        </div>
      )}

      {step === "application" && (
        <div>
          <h1>Loan Application</h1>
          <form onSubmit={handleLoanSubmit}>
            <div>
              <label>Monthly Income (€):</label>
              <input
                type="number"
                value={monthlyIncome}
                onChange={(e) => setMonthlyIncome(e.target.value)}
                required
              />
            </div>
            <div>
              <label>Monthly Expenses (€):</label>
              <input
                type="number"
                value={monthlyExpenses}
                onChange={(e) => setMonthlyExpenses(e.target.value)}
                required
              />
            </div>
            <button type="submit" style={{ marginTop: "1rem" }}>
              Submit Loan Application
            </button>
          </form>
          {message && <p style={{ color: "blue", marginTop: "1rem" }}>{message}</p>}
        </div>
      )}

      {loanResult && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Loan Application Result</h2>
          <p>Credit Score: {loanResult.credit_score}</p>
          <p>Application Status: {loanResult.status}</p>
        </div>
      )}
    </div>
  );
};

export default LoanApplication;
