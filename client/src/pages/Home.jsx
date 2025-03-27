import { useNavigate } from "react-router-dom";
import "../styles/Home.css";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <div className="home-content">
        <h1>Welcome to <span className="brand-name">ProxiHealth</span></h1>
        <p>Your health, your way. Please choose an option:</p>
        <div className="button-group">
          <button className="btn primary-btn" onClick={() => navigate("/login")}>User Login</button>
          <button className="btn secondary-btn" onClick={() => navigate("/register")}>User Register</button>
          <button className="btn doctor-btn" onClick={() => navigate("/login-doctor")}>Doctor Login</button>
          <button className="btn doctor-register-btn" onClick={() => navigate("/register-doctor")}>Register for Doctors</button>
        </div>
      </div>
    </div>
  );
}

export default Home;