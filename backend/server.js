require("dotenv").config();
const express = require("express");
const cors = require("cors");
const bcrypt = require("bcrypt");
const { Pool } = require("pg");
const { google } = require("googleapis");
const querystring = require("querystring");

const app = express();
const port = process.env.PORT || 5000;

app.use(cors({ origin: ["http://localhost:5174", "http://localhost:3000"], credentials: true }));
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

// ✅ Google OAuth2 Setup
const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI
);

// ✅ Step 1: Redirect User to Google Fit Login
app.get("/fit/auth", (req, res) => {
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: [
      "https://www.googleapis.com/auth/fitness.activity.read",
      "https://www.googleapis.com/auth/fitness.heart_rate.read",
    ],
  });
  res.redirect(authUrl);
});

// ✅ Step 2: Handle OAuth2 Callback
app.get("/fit/callback", async (req, res) => {
  const { code } = req.query;
  if (!code) return res.status(400).json({ message: "Authorization failed" });

  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    res.json({ message: "Google Fit Auth Successful", tokens });
  } catch (error) {
    console.error("Google Fit Auth Error:", error);
    res.status(500).json({ message: "Authentication failed" });
  }
});

// ✅ Step 3: Fetch Steps Data & Save to PostgreSQL
app.get("/fit/steps", async (req, res) => {
  try {
    oauth2Client.setCredentials({ access_token: req.query.access_token });

    const fitness = google.fitness({ version: "v1", auth: oauth2Client });

    const response = await fitness.users.dataset.aggregate({
      userId: "me",
      requestBody: {
        aggregateBy: [{ dataTypeName: "com.google.step_count.delta" }],
        bucketByTime: { durationMillis: 86400000 },
        startTimeMillis: Date.now() - 86400000, // Last 24 hours
        endTimeMillis: Date.now(),
      },
    });

    const steps = response.data.bucket[0]?.dataset[0]?.point[0]?.value[0]?.intVal || 0;

    // ✅ Save to PostgreSQL
    const email = "gliterry87@gmail.com"; // Replace with actual user email from session
    await pool.query("INSERT INTO steps (email, steps, date) VALUES ($1, $2, NOW())", [email, steps]);

    res.json({ steps });
  } catch (error) {
    console.error("Error fetching steps:", error);
    res.status(500).json({ message: "Failed to fetch steps" });
  }
});

// ✅ Step 4: Fetch Heart Rate Data & Save to PostgreSQL
app.get("/fit/heartrate", async (req, res) => {
  try {
    oauth2Client.setCredentials({ access_token: req.query.access_token });

    const fitness = google.fitness({ version: "v1", auth: oauth2Client });

    const response = await fitness.users.dataset.aggregate({
      userId: "me",
      requestBody: {
        aggregateBy: [{ dataTypeName: "com.google.heart_rate.bpm" }],
        bucketByTime: { durationMillis: 86400000 },
        startTimeMillis: Date.now() - 86400000,
        endTimeMillis: Date.now(),
      },
    });

    const heartRate = response.data.bucket[0]?.dataset[0]?.point[0]?.value[0]?.fpVal || 0;

    // ✅ Save to PostgreSQL
    const email = "gliterry87@gmail.com"; // Replace with actual user email from session
    await pool.query("INSERT INTO heart_rate (email, bpm, date) VALUES ($1, $2, NOW())", [email, heartRate]);

    res.json({ heartRate });
  } catch (error) {
    console.error("Error fetching heart rate:", error);
    res.status(500).json({ message: "Failed to fetch heart rate" });
  }
});

// ✅ Start Server
app.listen(port, () => {
  console.log(✅ Server running on http://localhost:${port});
});