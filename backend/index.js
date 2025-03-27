const express = require("express");
const cors = require("cors");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const pool = require("./db");
require("dotenv").config();

const app = express();
app.use(express.json());
app.use(cors());

const PORT = process.env.PORT || 5000;
const SECRET_KEY = "your_secret_key"; // Move to environment variables in production

// User Registration (Sign Up)
app.post("/register", async (req, res) => {
  const { name, age, gender, chronic_disease, email, password } = req.body;

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = await pool.query(
      "INSERT INTO users (name, age, gender, chronic_disease, email, password) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
      [name, age, gender, chronic_disease, email, hashedPassword]
    );
    res.json({ message: "User created successfully", user: newUser.rows[0] });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// User Login
app.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
    if (user.rows.length === 0) return res.status(400).json({ error: "User not found" });

    const isMatch = await bcrypt.compare(password, user.rows[0].password);
    if (!isMatch) return res.status(401).json({ error: "Invalid credentials" });

    const token = jwt.sign({ id: user.rows[0].id }, SECRET_KEY, { expiresIn: "1h" });
    res.json({ message: "Login successful", token, user: user.rows[0] });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get User Profile
app.get("/profile", async (req, res) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Unauthorized" });

  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    const user = await pool.query("SELECT * FROM users WHERE id = $1", [decoded.id]);

    if (user.rows.length === 0) return res.status(404).json({ error: "User not found" });

    res.json(user.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Start Server
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
