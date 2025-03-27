import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/Profile.css";

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [ip, setIp] = useState("");
  const [editing, setEditing] = useState(false);
  const [newDisease, setNewDisease] = useState("");
  const [diseaseOptions, setDiseaseOptions] = useState([]);

  const [accessToken, setAccessToken] = useState(localStorage.getItem("fit_access_token") || "");
  const [steps, setSteps] = useState(null);
  const [heartRate, setHeartRate] = useState(null);

  // ✅ Load User Data & Fetch IP
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
    } catch (err) {
      console.error("Error loading user data:", err);
      localStorage.removeItem("user");
      navigate("/login");
    }
  }, [navigate]);

  // ✅ Save Chronic Disease
  const handleSaveDisease = async () => {
    if (!newDisease) {
      alert("Please select a valid chronic disease.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/update-chronic-disease", {
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

  // ✅ Google Fit Authentication
  const connectGoogleFit = () => {
    window.location.href = "http://localhost:5000/fit/auth";
  };

  // ✅ Fetch Steps from Google Fit
  const fetchSteps = async () => {
    if (!accessToken) {
      alert("Please connect to Google Fit first.");
      return;
    }

    try {
      const res = await axios.get("http://localhost:5000/fit/steps", {
        params: { access_token: accessToken },
      });
      setSteps(res.data.steps);
    } catch (error) {
      console.error("Error fetching steps:", error);
      alert("Failed to fetch steps. Try reconnecting Google Fit.");
    }
  };

  // ✅ Fetch Heart Rate from Google Fit
  const fetchHeartRate = async () => {
    if (!accessToken) {
      alert("Please connect to Google Fit first.");
      return;
    }

    try {
      const res = await axios.get("http://localhost:5000/fit/heartrate", {
        params: { access_token: accessToken },
      });
      setHeartRate(res.data.heartRate);
    } catch (error) {
      console.error("Error fetching heart rate:", error);
      alert("Failed to fetch heart rate. Try reconnecting Google Fit.");
    }
  };

  // ✅ Logout
  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("fit_access_token");
    navigate("/");
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

            {editing ? (
              <>
                <select
                  value={newDisease}
                  onChange={(e) => setNewDisease(e.target.value)}
                  className="input-field"
                >
                  <option value="">Select Chronic Disease</option>
                  {diseaseOptions.map((disease, index) => (
                    <option key={index} value={disease}>{disease}</option>
                  ))}
                </select>
                <button className="btn" onClick={handleSaveDisease}>Save</button>
                <button className="btn cancel-btn" onClick={() => setEditing(false)}>Cancel</button>
              </>
            ) : (
              <button className="btn" onClick={() => setEditing(true)}>Edit Chronic Disease</button>
            )}

            <p><strong>Current IP:</strong> {ip || "Fetching..."}</p>

            {/* ✅ Google Fit Section */}
            <div className="google-fit">
              <h3>Google Fit Integration</h3>
              <button className="btn google-fit-btn" onClick={connectGoogleFit}>Connect Google Fit</button>
              <button className="btn" onClick={fetchSteps}>Fetch Steps</button>
              <button className="btn" onClick={fetchHeartRate}>Fetch Heart Rate</button>
              <p><strong>Steps:</strong> {steps !== null ? steps : "N/A"}</p>
              <p><strong>Heart Rate:</strong> {heartRate !== null ? heartRate : "N/A"}</p>
            </div>

            <button className="btn logout-btn" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <p>Loading profile...</p>
        )}
      </div>
    </div>
  );
};

export default Profile;
