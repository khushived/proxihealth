//RegisterD.jsx
// ✅ RegisterDoctor.jsx (New Doctor Registration Page)
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/Register.css";

const RegisterD = () => {
  const [doctor, setDoctor] = useState({ doctor_id: "D0", name: "", age: "", gender: "", email: "", password: "" });
  const navigate = useNavigate();

  const handleChange = (e) => {
    setDoctor({ ...doctor, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:5000/register-doctor", doctor);
      if (res.status === 201) {
        alert("Doctor registered successfully!");
        navigate("/login");
      }
    } catch (error) {
      alert(error.response?.data?.message || "Registration failed");
    }
  };

  return (
    <div className="register-container">
      <h2>Doctor Registration</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" name="doctor_id" value={doctor.doctor_id} onChange={handleChange} required placeholder="Doctor ID (Starts with D0)" />
        <input type="text" name="name" value={doctor.name} onChange={handleChange} required placeholder="Full Name" />
        <input type="number" name="age" value={doctor.age} onChange={handleChange} required placeholder="Age" />
        <select name="gender" value={doctor.gender} onChange={handleChange} required>
          <option value="">Select Gender</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
        </select>
        <input type="email" name="email" value={doctor.email} onChange={handleChange} required placeholder="Email" />
        <input type="password" name="password" value={doctor.password} onChange={handleChange} required placeholder="Password" />
        <button type="submit" className="btn">Register</button>
      </form>
    </div>
  );
};

export default RegisterD;
