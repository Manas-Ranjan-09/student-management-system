/**
 * API Client with Token Authentication and Error Handling
 */
const API = {
    getToken() {
        return localStorage.getItem('sms_auth_token');
    },

    setToken(token) {
        if (token) {
            localStorage.setItem('sms_auth_token', token);
        } else {
            localStorage.removeItem('sms_auth_token');
        }
    },

    getUser() {
        const u = localStorage.getItem('sms_user');
        return u ? JSON.parse(u) : null;
    },

    setUser(user) {
        if (user) {
            localStorage.setItem('sms_user', JSON.stringify(user));
        } else {
            localStorage.removeItem('sms_user');
        }
    },

    clearAuth() {
        localStorage.removeItem('sms_auth_token');
        localStorage.removeItem('sms_user');
    },

    async request(endpoint, options = {}) {
        const baseUrl = CONFIG.getApiBaseUrl();
        const url = `${baseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
        
        const headers = options.headers || {};
        if (!options.isFormData && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        options.headers = headers;

        try {
            const response = await fetch(url, options);

            // Handle 401 Unauthorized
            if (response.status === 401) {
                this.clearAuth();
                if (!window.location.pathname.endsWith('index.html') && !window.location.pathname.endsWith('/')) {
                    window.location.href = 'index.html';
                }
                throw new Error('Session expired or unauthorized. Please log in again.');
            }

            if (options.responseType === 'blob') {
                if (!response.ok) {
                    throw new Error(`Download failed with status ${response.status}`);
                }
                return await response.blob();
            }

            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const errorMsg = data.error || data.detail || (typeof data === 'object' ? Object.values(data).flat().join(', ') : 'Request failed');
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    get(endpoint, params = {}) {
        let url = endpoint;
        const query = new URLSearchParams();
        for (const [k, v] of Object.entries(params)) {
            if (v !== undefined && v !== null && v !== '') {
                query.append(k, v);
            }
        }
        const qs = query.toString();
        if (qs) {
            url += (url.includes('?') ? '&' : '?') + qs;
        }
        return this.request(url, { method: 'GET' });
    },

    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    async download(endpoint, defaultFilename = 'download') {
        const blob = await this.request(endpoint, {
            method: 'GET',
            responseType: 'blob'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = defaultFilename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    }
};
