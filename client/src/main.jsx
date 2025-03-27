import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { GoogleOAuthProvider } from "@react-oauth/google";

const clientId = "912326922512-ub72jl05a0g7t9gtbv6jjqdj6gjof36s.apps.googleusercontent.com"; // Ensure it's the same as in backend

const root = createRoot(document.getElementById("root"));
root.render(
  <GoogleOAuthProvider clientId={clientId}>
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </GoogleOAuthProvider>
);
