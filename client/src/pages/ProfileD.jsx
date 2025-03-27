//ProfileD.jsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bar, Pie, Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from "chart.js";
import "../styles/Profile.css";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement);

const ProfileD = () => {
  const navigate = useNavigate();
  const [doctor, setDoctor] = useState(null);
  const [data, setData] = useState({ patients: [], analysis: {} });

  useEffect(() => {
    const storedDoctor = localStorage.getItem("doctor");
    if (!storedDoctor) {
      alert("Access denied! Redirecting to Doctor Login.");
      navigate("/login-doctor");
      return;
    }
    setDoctor(JSON.parse(storedDoctor));
    fetchDoctorData();
    const interval = setInterval(fetchDoctorData, 2 * 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, [navigate]);

  const fetchDoctorData = async () => {
    try {
      const res = await axios.get("http://localhost:5000/doctor-dashboard");
      setData(res.data);
    } catch (error) {
      console.error("Error fetching doctor dashboard data:", error);
    }
  };

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

      <div className="doctor-dashboard">
        <h1>Doctor's Dashboard</h1>
        <div className="card">
          <h2>Health Statistics</h2>
          <p><strong>Average Heart Rate:</strong> {data.analysis.avgHeartRate?.toFixed(2) || "Loading..."} BPM</p>
          <p><strong>Most Common Condition:</strong> {data.analysis.mostCommonCondition || "Loading..."}</p>
        </div>

        <div className="charts">
          <h2>Patient Data Trends</h2>
          <div className="chart">
            <h3>Patient Age Distribution</h3>
            <Bar
              data={{
                labels: [...new Set(data.patients.map((p) => p.age))],
                datasets: [{
                  label: "Number of Patients",
                  data: [...new Set(data.patients.map((p) => p.age))].map(
                    (age) => data.patients.filter((p) => p.age === age).length
                  ),
                  backgroundColor: "rgba(54, 162, 235, 0.6)",
                }],
              }}
              options={{ responsive: true }}
            />
          </div>

          <div className="chart">
            <h3>Most Common Conditions</h3>
            <Pie
              data={{
                labels: Object.keys(data.analysis.mostCommonCondition || {}),
                datasets: [{
                  data: Object.values(data.analysis.mostCommonCondition || {}),
                  backgroundColor: ["red", "blue", "green", "orange", "purple"],
                }],
              }}
            />
          </div>

          <div className="chart">
            <h3>Heart Rate Trends Over Time</h3>
            <Line
              data={{
                labels: data.patients.map((p) => p.date),
                datasets: [{
                  label: "Heart Rate (BPM)",
                  data: data.patients.map((p) => p.bpm),
                  borderColor: "red",
                  fill: false,
                }],
              }}
              options={{ responsive: true }}
            />
          </div>
        </div>

        <div className="data-table">
          <h2>All Patients' Data</h2>
          <table>
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Condition</th>
                <th>Heart Rate (BPM)</th>
                <th>Steps</th>
              </tr>
            </thead>
            <tbody>
              {data.patients.length > 0 ? (
                data.patients.map((p, index) => (
                  <tr key={index}>
                    <td>{p.patient_id}</td>
                    <td>{p.age}</td>
                    <td>{p.gender}</td>
                    <td>{p.condition}</td>
                    <td>{p.bpm}</td>
                    <td>{p.steps}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">Loading data...</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ProfileD;