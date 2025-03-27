//Profile.jsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Pie, Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from "chart.js";
import "../styles/Profile.css";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement);

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [ip, setIp] = useState("Fetching...");
  const [editing, setEditing] = useState(false);
  const [newDisease, setNewDisease] = useState("");
  const [diseaseOptions, setDiseaseOptions] = useState([]);
  const [isSavingIp, setIsSavingIp] = useState(false);
  const [data, setData] = useState({ diseasePrediction: {}, locationAlerts: [], stats: [] });

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      alert("Session expired. Redirecting to login.");
      navigate("/login");
      return;
    }

    try {
      const userData = JSON.parse(storedUser);
      setUser(userData);
      setNewDisease(userData.chronic_disease || "None");

      axios.get("https://api64.ipify.org?format=json")
        .then((res) => setIp(res.data.ip))
        .catch(() => setIp("Error fetching IP"));

      axios.get("http://localhost:5000/chronic-diseases")
        .then((res) => setDiseaseOptions(res.data))
        .catch(() => console.error("Failed to load chronic disease options"));

      fetchProfileData();
      const interval = setInterval(fetchProfileData, 2 * 60 * 60 * 1000);
      return () => clearInterval(interval);
    } catch (err) {
      console.error("Error loading user data:", err);
      localStorage.removeItem("user");
      navigate("/login");
    }
  }, [navigate]);

  const fetchProfileData = async () => {
    try {
      const res = await axios.get("http://localhost:5000/profile-data");
      setData(res.data);
    } catch (error) {
      console.error("Error fetching profile data:", error);
    }
  };

  const handleSaveDisease = async () => {
    if (!newDisease) {
      alert("Please select a valid chronic disease.");
      return;
    }

    try {
      const response = await axios.put("http://localhost:5000/update-chronic-disease", {
        email: user.email,
        chronic_disease: newDisease,
      });

      if (response.status === 200) {
        alert("Chronic disease updated successfully!");
        const updatedUser = { ...user, chronic_disease: newDisease };
        setUser(updatedUser);
        localStorage.setItem("user", JSON.stringify(updatedUser));
        setEditing(false);
      }
    } catch (error) {
      alert("Failed to update chronic disease.");
    }
  };

  const saveIpDetails = async () => {
    if (!ip || ip === "Error fetching IP") {
      alert("IP address not available.");
      return;
    }

    setIsSavingIp(true);
    try {
      const response = await axios.post("http://localhost:5000/save-ip", {
        email: user.email,
        ip_address: ip,
      });
      if (response.status === 200) alert("IP address saved successfully!");
      else alert("Error saving IP address.");
    } catch (error) {
      console.error("Error saving IP details:", error);
      alert("Failed to save IP details.");
    }
    setIsSavingIp(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h2>Profile</h2>
        {user ? (
          <>
            <p><strong>Name:</strong> {user.name}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Age:</strong> {user.age}</p>
            <p><strong>Gender:</strong> {user.gender}</p>
            <p><strong>IP Address:</strong> {ip}</p>

            {editing ? (
              <>
                <label>Chronic Disease:</label>
                <select value={newDisease} onChange={(e) => setNewDisease(e.target.value)} className="input-field">
                  <option value="">Select Chronic Disease</option>
                  {diseaseOptions.map((disease, index) => <option key={index} value={disease}>{disease}</option>)}
                </select>
                <button className="btn" onClick={handleSaveDisease}>Save</button>
                <button className="btn cancel-btn" onClick={() => setEditing(false)}>Cancel</button>
              </>
            ) : (
              <>
                <p><strong>Chronic Disease:</strong> {user.chronic_disease || "Not provided"}</p>
                <button className="btn" onClick={() => setEditing(true)}>Edit Chronic Disease</button>
              </>
            )}
            <button className="btn save-ip-btn" onClick={saveIpDetails} disabled={isSavingIp}>{isSavingIp ? "Saving..." : "Save IP Address"}</button>
            <button className="btn logout-btn" onClick={handleLogout}>Logout</button>
          </>
        ) : <p>Loading profile...</p>}
      </div>

      <h1>Health Dashboard</h1>
      <div className="card">
        <h2>Disease Prediction</h2>
        <p><strong>Predicted Condition:</strong> {data.diseasePrediction.condition || "Loading..."}</p>
        <p><strong>Risk Level:</strong> {data.diseasePrediction.risk || "Loading..."}</p>
      </div>
      <div className="card">
        <h2>Location Alerts</h2>
        <ul>
          {data.locationAlerts.length > 0 ? data.locationAlerts.map((alert, index) => <li key={index}>{alert}</li>) : <p>No alerts in your area.</p>}
        </ul>
      </div>
      <div className="charts">
        <h2>Health Data Insights</h2>
        <Bar data={{ labels: data.stats.map(d => d.date), datasets: [{ label: "Steps", data: data.stats.map(d => d.steps), backgroundColor: "rgba(75,192,192,0.6)" }] }} options={{ responsive: true }} />
        <Pie data={{ labels: ["Resting", "Fat Burn", "Cardio", "Peak"], datasets: [{ data: [30, 25, 25, 20], backgroundColor: ["blue", "green", "orange", "red"] }] }} />
        <Line data={{ labels: data.stats.map(d => d.date), datasets: [{ label: "Heart Rate (BPM)", data: data.stats.map(d => d.bpm), borderColor: "red", fill: false }] }} options={{ responsive: true }} />
      </div>
    </div>
  );
};

export default Profile;