import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";
function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5000/api/register", { email, password });
      setMessage("Registration successful!");
      setSuccess(true);
      setTimeout(() => navigate("/"), 2000);
    } catch (error) {
      setMessage("Registration failed. Email may already exist.");
      setSuccess(false);
    }
  };
  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-icon">🌱</span>
          <h2>Create Account</h2>
          <p>Join the Crop Advisory System</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <span className="input-icon">📧</span>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <span className="input-icon">🔒</span>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="auth-btn">Register</button>
        </form>
        {message && <p className={success ? "success-msg" : "error-msg"}>{message}</p>}
        <p className="auth-footer">Already have an account? <Link to="/">Login</Link></p>
      </div>
    </div>
  );
}
export default Register;