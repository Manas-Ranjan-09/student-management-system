/**
 * Global Configuration for Netlify Frontend
 * Configure your Render Backend API URL here or via the UI settings modal.
 */
const CONFIG = {
    // Default fallback backend URL (Render production URL or local development)
    DEFAULT_API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://student-management-system.onrender.com',

    getApiBaseUrl() {
        return localStorage.getItem('sms_api_base_url') || this.DEFAULT_API_URL;
    },

    setApiBaseUrl(url) {
        if (!url) {
            localStorage.removeItem('sms_api_base_url');
        } else {
            // Remove trailing slash if present
            url = url.replace(/\/+$/, '');
            localStorage.setItem('sms_api_base_url', url);
        }
    }
};
