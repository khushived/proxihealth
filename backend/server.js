require("dotenv").config();
const express = require("express");
const cors = require("cors");
const bcrypt = require("bcrypt");
const { Pool } = require("pg");
const axios = require("axios");

const app = express();
const port = process.env.PORT || 5000;

// ✅ Middleware
app.use(cors());
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

// ✅ Check Database Connection on Startup
pool.connect()
  .then(() => console.log("✅ Database connected successfully!"))
  .catch((err) => {
    console.error("❌ Database connection error:", err);
    process.exit(1);
  });

// ✅ Register Route
app.post("/register", async (req, res) => {
  try {
    const { name, age, gender, chronic_disease, email, password } = req.body;

    if (!name || !age || !gender || !chronic_disease || !email || !password) {
      return res.status(400).json({ message: "All fields are required" });
    }

    const userExists = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: "User already exists!" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = await pool.query(
      "INSERT INTO users (name, age, gender, chronic_disease, email, password) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
      [name, age, gender, chronic_disease, email, hashedPassword]
    );

    res.status(201).json({ message: "User registered successfully!", user: newUser.rows[0] });
  } catch (error) {
    console.error("❌ Registration Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

// ✅ Login Route
app.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await pool.query("SELECT * FROM users WHERE email = $1", [email]);

    if (user.rows.length === 0) {
      return res.status(400).json({ message: "User not found!" });
    }

    const isMatch = await bcrypt.compare(password, user.rows[0].password);
    if (!isMatch) {
      return res.status(401).json({ message: "Invalid email or password" });
    }

    res.status(200).json({
      message: "Login successful",
      user: {
        id: user.rows[0].id,
        name: user.rows[0].name,
        age: user.rows[0].age,
        gender: user.rows[0].gender,
        chronic_disease: user.rows[0].chronic_disease,
        email: user.rows[0].email,
      },
    });

  } catch (error) {
    console.error("Login Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

// ✅ Save IP Address with Full Details
app.post("/save-ip", async (req, res) => {
  try {
    const { email, ip_address } = req.body;

    // Ensure the email exists
    const user = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (user.rows.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    // Fetch IP Geolocation Data
    const geoResponse = await axios.get(`http://ip-api.com/json/${ip_address}`);
    const geoData = geoResponse.data;

    if (geoData.status !== "success") {
      return res.status(400).json({ message: "Failed to fetch IP details" });
    }

    // Insert Full IP Data into `ip_info`
    await pool.query(
      `INSERT INTO ip_info (user_email, ip_address, latitude, longitude, city, region, country, isp, created_at) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())`,
      [
        email,
        ip_address,
        geoData.lat,
        geoData.lon,
        geoData.city,
        geoData.regionName,
        geoData.country,
        geoData.isp,
      ]
    );

    res.status(200).json({ message: "IP address saved successfully with full details!" });
  } catch (error) {
    console.error("❌ IP Save Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});

// ✅ Start Server
app.listen(port, () => {
  console.log(`✅ Server running on http://localhost:${port}`);
});
