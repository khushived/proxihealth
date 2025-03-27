//App.jsx

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
  const [authStatus, setAuthStatus] = useState({
    user: JSON.parse(localStorage.getItem("user")) || null,
    doctor: JSON.parse(localStorage.getItem("doctor")) || null,
  });

  // ✅ Periodically check localStorage changes every second
  useEffect(() => {
    const interval = setInterval(() => {
      setAuthStatus({
        user: JSON.parse(localStorage.getItem("user")) || null,
        doctor: JSON.parse(localStorage.getItem("doctor")) || null,
      });
    }, 1000); // Check every second

    return () => clearInterval(interval);
  }, []);

  const isAuthenticated = !!authStatus.user;
  const isDoctorAuthenticated = !!authStatus.doctor;

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/profile" replace /> : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/profile" replace /> : <Register />} />
          <Route path="/register-doctor" element={isDoctorAuthenticated ? <Navigate to="/doctor-profile" replace /> : <RegisterD />} />
          <Route path="/login-doctor" element={isDoctorAuthenticated ? <Navigate to="/doctor-profile" replace /> : <LoginD />} />

          {/* ✅ Protected Routes */}
          <Route path="/profile" element={isAuthenticated ? <Profile /> : <Navigate to="/login" replace />} />
          <Route path="/doctor-profile" element={isDoctorAuthenticated ? <ProfileD /> : <Navigate to="/login-doctor" replace />} />

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