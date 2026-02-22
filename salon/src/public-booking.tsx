/**
 * Public Booking Entry Point
 * This is the entry point for the public booking application
 * served via subdomain (e.g., acme-salon.kenikool.com)
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import PublicBookingApp from "./PublicBookingApp.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <PublicBookingApp />
  </StrictMode>,
);
