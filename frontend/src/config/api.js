// Centralized API base URL for frontend
// Uses Vite environment variable VITE_BACKEND_URL when available,
// otherwise falls back to localhost for local development.
// IMPORTANT: Vite only exposes env vars prefixed with VITE_ to the client bundle.
// Try build-time Vite variable first. If the site was deployed without
// rebuilding (or you want to override at runtime), the code will also check
// for a runtime global `window.__MAPENU_BACKEND_URL__` or a meta tag:
// <meta name="backend-url" content="https://mapenu.onrender.com">.
const API_BASE_URL =
	import.meta.env.VITE_BACKEND_URL ||
	(typeof window !== "undefined" && window.__VITE_BACKEND_URL__) ||
	(typeof document !== "undefined" && document.querySelector('meta[name="vite-backend-url"]')?.content) ||
	"http://localhost:8000";

// Debug: uncomment to log the resolved API base used by the client.
// console.log("API_BASE_URL:", API_BASE_URL);

export default API_BASE_URL;
