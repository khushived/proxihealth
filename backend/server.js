//Updated server.js

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const bcrypt = require("bcrypt");
const { Pool } = require("pg");
const { exec } = require("child_process");

const app = express();
const port = process.env.PORT || 5000;

// ✅ Middleware
app.use(cors({ origin: ["http://localhost:5174", "http://localhost:5000"], credentials: true }));
app.use(express.json());

// ✅ PostgreSQL Database Connection
const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT || 5432,
  ssl: { rejectUnauthorized: false },
});

pool.connect()
  .then(() => console.log("✅ Database connected successfully!"))
  .catch((err) => {
    console.error("❌ Database connection error:", err);
    process.exit(1);
  });

// ✅ Doctor Login Route
app.post("/login-doctor", async (req, res) => {
  const { doctor_id, password } = req.body;
  try {
    const result = await pool.query("SELECT * FROM doctors WHERE doctor_id = $1", [doctor_id]);
    if (result.rows.length === 0) {
      return res.status(400).json({ message: "Invalid Doctor ID or Password" });
    }
    const doctor = result.rows[0];
    const passwordMatch = await bcrypt.compare(password, doctor.password);
    if (!passwordMatch) {
      return res.status(400).json({ message: "Invalid Doctor ID or Password" });
    }
    res.status(200).json({ message: "Login successful", doctor });
  } catch (error) {
    console.error("❌ Doctor Login Error:", error);
    res.status(500).json({ message: "Internal Server Error" });
  }
});

// ✅ Doctor Registration Route
app.post("/register-doctor", async (req, res) => {
  const { doctor_id, name, age, gender, email, password } = req.body;
  if (!doctor_id.startsWith("D0")) {
      return res.status(400).json({ message: "Doctor ID must start with 'D0'" });
  }
  try {
      const existingDoctor = await pool.query("SELECT * FROM doctors WHERE doctor_id = $1", [doctor_id]);
      if (existingDoctor.rows.length > 0) {
          return res.status(400).json({ message: "Doctor ID already registered" });
      }
      const hashedPassword = await bcrypt.hash(password, 10);
      await pool.query(
          "INSERT INTO doctors (doctor_id, name, age, gender, email, password) VALUES ($1, $2, $3, $4, $5, $6)",
          [doctor_id, name, age, gender, email, hashedPassword]
      );
      res.status(201).json({ message: "Doctor registered successfully!" });
  } catch (error) {
      console.error("❌ Doctor Registration Error:", error);
      res.status(500).json({ message: "Error registering doctor", error });
  }
});

// ✅ User Registration Route
app.post("/register-user", async (req, res) => {
  const { name, age, gender, chronic_disease, email, password } = req.body;
  try {
    const userExists = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: "Email already registered" });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    await pool.query(
      "INSERT INTO users (name, age, gender, chronic_disease, email, password) VALUES ($1, $2, $3, $4, $5, $6)",
      [name, age, gender, chronic_disease, email, hashedPassword]
    );
    res.status(201).json({ message: "User registered successfully!" });
  } catch (error) {
    console.error("❌ User Registration Error:", error);
    res.status(500).json({ message: "Error registering user", error });
  }
});

// ✅ User Login Route
app.post("/login-user", async (req, res) => {
  const { email, password } = req.body;
  try {
    const result = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (result.rows.length === 0) {
      return res.status(400).json({ message: "Invalid Email or Password" });
    }
    const user = result.rows[0];
    const passwordMatch = await bcrypt.compare(password, user.password);
    if (!passwordMatch) {
      return res.status(400).json({ message: "Invalid Email or Password" });
    }
    res.status(200).json({ message: "Login successful", user });
  } catch (error) {
    console.error("❌ User Login Error:", error);
    res.status(500).json({ message: "Internal Server Error" });
  }
});

// ✅ Fetch Predictions & Alerts
app.get("/profile-data", async (req, res) => {
  try {
    exec("python3 disease_prediction.py", (error, stdout) => {
      if (error) {
        console.error("Error executing disease prediction:", error);
        return res.status(500).json({ message: "Failed to fetch predictions" });
      }
      const diseasePrediction = JSON.parse(stdout);
      exec("python3 location_matcher.py", async (err, locationOutput) => {
        if (err) {
          console.error("Error executing location matcher:", err);
          return res.status(500).json({ message: "Failed to fetch location alerts" });
        }
        const locationAlerts = JSON.parse(locationOutput);
        const { rows: stats } = await pool.query("SELECT * FROM health_data");
        res.json({ diseasePrediction, locationAlerts, stats });
      });
    });
  } catch (err) {
    res.status(500).json({ message: "Error fetching profile data", error: err.message });
  }
});

// ✅ Doctor Dashboard Route
app.get("/doctor-dashboard", async (req, res) => {
  try {
    const { rows: patients } = await pool.query("SELECT * FROM health_data");
    const avgHeartRate = patients.reduce((sum, p) => sum + p.bpm, 0) / patients.length;
    const mostCommonCondition = patients.map((p) => p.condition).reduce((acc, curr) => ((acc[curr] = (acc[curr] || 0) + 1), acc), {});
    const analysis = {
      avgHeartRate,
      mostCommonCondition: Object.keys(mostCommonCondition).reduce((a, b) => (mostCommonCondition[a] > mostCommonCondition[b] ? a : b), ""),
    };
    res.json({ patients, analysis });
  } catch (err) {
    res.status(500).json({ message: "Error fetching doctor dashboard data", error: err.message });
  }
});

// ✅ Start Express Server
app.listen(port, () => {
  console.log("✅ Server running on http://localhost:${port}");
});