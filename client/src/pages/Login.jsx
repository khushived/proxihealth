//Login.jsx

import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { jwtDecode } from "jwt-decode";
import "../styles/Login.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // ✅ Handle Manual Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const res = await axios.post(
        "http://localhost:5000/login-user",
        { email, password },
        { withCredentials: true }
      );

      console.log("Server Response:", res.data);

      if (res.status === 200 && res.data.user) {
        localStorage.setItem("user", JSON.stringify(res.data.user));
        console.log("User stored in localStorage:", localStorage.getItem("user"));
        alert("Login successful!");
        navigate("/profile"); // ✅ Redirect to Profile
      } else {
        setError("Unexpected response format from server.");
      }
    } catch (err) {
      console.error("Login Error:", err);
      setError(err.response?.data?.message || "Invalid email or password. Please try again.");
    }
  };

  // ✅ Handle Google Login Success
  const handleGoogleSuccess = async (response) => {
    if (!response || !response.credential) {
      setError("Google login failed. Please try again.");
      return;
    }

    const decoded = jwtDecode(response.credential);
    console.log("Decoded Google User:", decoded);

    try {
      const res = await axios.post(
        "http://localhost:5000/google-login-user",
        { token: response.credential },
        {
          withCredentials: true,
          headers: { Authorization: `Bearer ${response.credential}` }
        }
      );

      console.log("Google Login Response:", res.data);

      if (res.status === 200 && res.data.user) {
        localStorage.setItem("user", JSON.stringify(res.data.user));
        console.log("User stored in localStorage:", localStorage.getItem("user"));
        navigate("/profile"); // ✅ Redirect to Profile
      } else {
        setError("Unexpected response format from Google authentication.");
      }
    } catch (err) {
      console.error("Google Login Error:", err);
      setError(err.response?.data?.message || "Google authentication error. Please try again.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        {error && <p className="error-text">{error}</p>}

        {/* ✅ Standard Login Form */}
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="btn">Login</button>
        </form>

        {/* ✅ Google Login Button */}
        <div className="google-login">
          <h3>Or login with Google</h3>
          <GoogleLogin 
            onSuccess={handleGoogleSuccess} 
            onError={() => setError("Google login failed. Please try again.")} 
          />
        </div>
      </div>
    </div>
  );
};

export default Login;