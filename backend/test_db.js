const pool = require("./db"); // Ensure db.js exists in the backend folder

async function testConnection() {
  try {
    const res = await pool.query("SELECT NOW()");
    console.log("✅ Database connected at:", res.rows[0].now);
  } catch (error) {
    console.error("❌ Database connection error:", error);
  }
}

testConnection();
