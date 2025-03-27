import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { useState, useEffect } from "react";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import RegisterD from "./pages/RegisterD";
import LoginD from "./pages/LoginD";
import ProfileD from "./pages/ProfileD";

// 🔹 Replace with your actual Google Client ID from Google Cloud Console
const GOOGLE_CLIENT_ID = "912326922512-ub72jl05a0g7t9gtbv6jjqdj6gjof36s.apps.googleusercontent.com";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("user"));
  const [isDoctorAuthenticated, setIsDoctorAuthenticated] = useState(!!localStorage.getItem("doctor"));

  useEffect(() => {
    console.log("🔍 Checking authentication status...");
    
    // ✅ Function to update authentication status dynamically
    const handleAuthChange = () => {
      setIsAuthenticated(!!localStorage.getItem("user"));
      setIsDoctorAuthenticated(!!localStorage.getItem("doctor"));
    };

    window.addEventListener("storage", handleAuthChange);

    return () => {
      window.removeEventListener("storage", handleAuthChange);
    };
  }, []);

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/register-doctor" element={<RegisterD />} />
          <Route path="/login-doctor" element={<LoginD />} />

          {/* ✅ Protected Routes */}
          <Route path="/profile" element={isAuthenticated ? <Profile /> : <Navigate to="/login" />} />
          <Route path="/doctor-profile" element={isDoctorAuthenticated ? <ProfileD /> : <Navigate to="/login-doctor" />} />

          {/* ✅ 404 Page Handling */}
          <Route
            path="*"
            element={
              <div style={{ textAlign: "center", padding: "50px" }}>
                <h1 style={{ color: "red" }}>404 - Page Not Found</h1>
                <p>The page you are looking for does not exist.</p>
                <a href="/" style={{ color: "blue", textDecoration: "underline" }}>Go to Home</a>
              </div>
            }
          />
        </Routes>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
