import { useNavigate } from "react-router-dom";
import "../styles/Home.css";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      {/* Animated Bubbles */}
      <div className="bubble"></div>
      <div className="bubble"></div>
      <div className="bubble"></div>
      <div className="bubble"></div>
      <div className="bubble"></div>

      <div className="home-content">
        <h1>Welcome to <span className="brand-name">ProxiHealth</span></h1>
        <p>Your health, your way. Please choose an option:</p>
        <div className="button-group">
          <button className="btn primary-btn" onClick={() => navigate("/login")}>Login</button>
          <button className="btn secondary-btn" onClick={() => navigate("/register")}>Create Account</button>
        </div>
      </div>
    </div>
  );
}

export default Home;
