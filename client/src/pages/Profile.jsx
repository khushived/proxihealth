import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/Profile.css"; // Import styles

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [ip, setIp] = useState("");

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      alert("Failed to load profile. Redirecting to login.");
      navigate("/login");
      return;
    }

    setUser(JSON.parse(storedUser));

    axios.get("https://api64.ipify.org?format=json")
      .then((res) => setIp(res.data.ip))
      .catch((err) => console.error("Error fetching IP:", err));
  }, [navigate]);

  const handleSaveIP = async () => {
    try {
      await axios.post("http://localhost:5000/save-ip", {
        email: user.email,
        ip_address: ip,
      });
      alert("IP address saved successfully!");
    } catch (error) {
      alert("Failed to save IP address.");
    }
  };

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h2>Profile</h2>
        {user ? (
          <>
            <p><strong>Name:</strong> {user.name}</p>
            <p><strong>Age:</strong> {user.age}</p>
            <p><strong>Gender:</strong> {user.gender}</p>
            <p><strong>Chronic Disease:</strong> {user.chronic_disease}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Current IP:</strong> {ip}</p>
            <button className="btn" onClick={handleSaveIP}>Save IP Address</button>
          </>
        ) : (
          <p>Loading profile...</p>
        )}
      </div>
    </div>
  );
};

export default Profile;
