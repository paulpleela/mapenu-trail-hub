// Centralized API base URL for frontend
// Uses Vite environment variable BACKEND_URL when available,
// otherwise falls back to localhost for local development.
const API_BASE_URL = import.meta.env.BACKEND_URL || "http://localhost:8000";

export default API_BASE_URL;
