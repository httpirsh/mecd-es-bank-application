import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// Function to get CSRF token from cookies
function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return null;
}

const LoanApplication = () => {
  const [loanConfiguration, setLoanConfiguration] = useState(null);
  const [monthlyIncome, setMonthlyIncome] = useState("");
  const [monthlyExpenses, setMonthlyExpenses] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false); // State to handle loading
  const navigate = useNavigate();

  // Load loan configuration from localStorage
  useEffect(() => {
    const storedConfig = localStorage.getItem("loan_configuration");
    if (storedConfig) {
      setLoanConfiguration(JSON.parse(storedConfig));
    }
  }, []);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setIsLoading(true);  // Start loading when form is submitted

    // Validate required fields
    if (!monthlyIncome || !monthlyExpenses) {
      setError("Please enter both monthly income and expenses.");
      setIsLoading(false); // Stop loading
      return;
    }

    try {
      const response = await fetch("/api/loan-application/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),  // Include CSRF token
        },
        body: JSON.stringify({
          monthly_income: parseFloat(monthlyIncome),
          monthly_expenses: parseFloat(monthlyExpenses),
          loan_amount: loanConfiguration.loan_amount,
          loan_duration: loanConfiguration.loan_duration,
        }),
      });

      if (!response.ok) {
        // Check if response is not OK
        const errorData = await response.text(); // Get response as text in case of error
        throw new Error(errorData || "An unexpected error occurred.");
      }

      // Parse the JSON response
      const data = await response.json();
      setResult(data);

      // Show the result based on the application status
      if (data.application_status === "accept") {
        alert("Loan application approved!");
      } else if (data.application_status === "interview") {
        alert("Loan requires further review.");
      } else {
        alert("Loan application rejected.");
      }
    } catch (err) {
      setError(err.message || "Error during loan application.");
    } finally {
      setIsLoading(false);  // Stop loading after the request is done
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "2rem" }}>
      <h1>Loan Application</h1>
      {loanConfiguration ? (
        <div>
          <h2>Loan Details</h2>
          <p>Loan Amount: €{loanConfiguration.loan_amount}</p>
          <p>Loan Duration: {loanConfiguration.loan_duration} months</p>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: "1rem" }}>
              <label htmlFor="monthlyIncome">Monthly Income (€):</label>
              <input
                type="number"
                id="monthlyIncome"
                value={monthlyIncome}
                onChange={(e) => setMonthlyIncome(e.target.value)}
                required
              />
            </div>
            <div style={{ marginBottom: "1rem" }}>
              <label htmlFor="monthlyExpenses">Monthly Expenses (€):</label>
              <input
                type="number"
                id="monthlyExpenses"
                value={monthlyExpenses}
                onChange={(e) => setMonthlyExpenses(e.target.value)}
                required
              />
            </div>
            <button type="submit" disabled={isLoading}>Submit Application</button>
          </form>

          {isLoading && <p>Loading...</p>}  {/* Display loading state */}
          {error && <p style={{ color: "red" }}>{error}</p>}
          {result && (
            <div>
              <h3>Application Status</h3>
              <p>Credit Score: {result.credit_score}</p>
              <p>Status: {result.application_status}</p>
            </div>
          )}
        </div>
      ) : (
        <p>Loading loan details...</p>
      )}
    </div>
  );
};

export default LoanApplication;
