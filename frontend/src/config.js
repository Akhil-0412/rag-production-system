
const getApiUrl = () => {
    let url = import.meta.env.VITE_API_URL;

    if (!url) {
        return "http://localhost:8000/api";
    }

    // If provided as just a hostname (from Render), add protocol
    if (!url.startsWith("http")) {
        url = `https://${url}`;
    }

    // Ensure /api suffix
    if (!url.endsWith("/api")) {
        // Remove trailing slash if present to avoid double //
        if (url.endsWith("/")) {
            url = url.slice(0, -1);
        }
        url = `${url}/api`;
    }

    return url;
};

export const API_URL = getApiUrl();
