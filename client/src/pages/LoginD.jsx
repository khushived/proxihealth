//LoginD.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/Login.css"; // Ensure correct styling

const LoginD = () => {
  const [doctor_id, setDoctorId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const res = await axios.post("http://localhost:5000/login-doctor", { doctor_id, password });

      if (res.status === 200) {
        localStorage.setItem("doctor", JSON.stringify(res.data.doctor));
        alert("Login successful!");

        // ✅ Force page refresh to ensure navigation updates
        window.location.href = "/doctor-profile";
      } else {
        setError(res.data.message || "Login failed");
      }
    } catch (error) {
      setError("Invalid Doctor ID or Password");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Doctor Login</h2>
        {error && <p className="error-text">{error}</p>}
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Doctor ID"
            value={doctor_id}
            onChange={(e) => setDoctorId(e.target.value)}
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
      </div>
    </div>
  );
};

export default LoginD;

