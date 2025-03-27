//ProfileD.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/Profile.css"; // Reuse the same styling as Profile

const ProfileD = () => {
  const navigate = useNavigate();
  const [doctor, setDoctor] = useState(null);

  useEffect(() => {
    const storedDoctor = localStorage.getItem("doctor");
    if (!storedDoctor) {
      alert("Access denied! Redirecting to Doctor Login.");
      navigate("/login-doctor");
      return;
    }

    const doctorData = JSON.parse(storedDoctor);
    setDoctor(doctorData);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("doctor");
    navigate("/");
  };

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h2>Doctor Profile</h2>
        {doctor ? (
          <>
            <p><strong>Doctor ID:</strong> {doctor.doctor_id}</p>
            <p><strong>Name:</strong> {doctor.name}</p>
            <p><strong>Age:</strong> {doctor.age}</p>
            <p><strong>Gender:</strong> {doctor.gender}</p>
            <p><strong>Email:</strong> {doctor.email}</p>
            <button className="btn logout-btn" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <p>Loading profile...</p>
        )}
      </div>
    </div>
  );
};

export default ProfileD;

