// Centralized API base URL for frontend
// Uses Vite environment variable VITE_BACKEND_URL when available,
// otherwise falls back to localhost for local development.
// IMPORTANT: Vite only exposes env vars prefixed with VITE_ to the client bundle.
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

// Debug: leave this commented during normal runs. Uncomment to print the
// resolved API_BASE_URL in the browser console for quick debugging.
// console.log("API_BASE_URL:", API_BASE_URL);

export default API_BASE_URL;
