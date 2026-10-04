/**
 * Auth controller, Theme manager, and UI Toasts
 */
const UI = {
    showToast(message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast-item ${type}`;

        const iconMap = {
            success: 'fa-check-circle text-success',
            error: 'fa-exclamation-circle text-danger',
            info: 'fa-info-circle text-primary'
        };

        toast.innerHTML = `
            <i class="fas ${iconMap[type] || iconMap.info} fa-lg"></i>
            <div style="flex: 1; font-weight: 500; font-size: 0.9rem;">${message}</div>
            <button onclick="this.parentElement.remove()" style="background:none; border:none; color:var(--text-muted); cursor:pointer;">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    },

    initTheme() {
        const savedTheme = localStorage.getItem('sms_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeToggleIcons(savedTheme);
    },

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('sms_theme', newTheme);
        this.updateThemeToggleIcons(newTheme);
    },

    updateThemeToggleIcons(theme) {
        document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
            btn.innerHTML = theme === 'dark' 
                ? '<i class="fas fa-sun text-warning"></i>' 
                : '<i class="fas fa-moon text-secondary"></i>';
        });
    },

    // Backend URL configuration modal
    openBackendConfigModal() {
        const currentUrl = CONFIG.getApiBaseUrl();
        const modal = document.createElement('div');
        modal.className = 'modal-backdrop-custom show';
        modal.id = 'backend-config-modal';
        modal.innerHTML = `
            <div class="modal-content-custom" style="padding: 1.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                    <h4 style="margin: 0;"><i class="fas fa-server me-2 text-primary"></i>Backend API URL</h4>
                    <button onclick="document.getElementById('backend-config-modal').remove()" style="background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--text-muted);">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1.25rem;">
                    When deployed on <strong>Netlify</strong>, set this to your live <strong>Render Backend URL</strong> (e.g. <code>https://your-service.onrender.com</code>).
                </p>
                <div style="margin-bottom: 1.25rem;">
                    <label style="display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.5rem;">API Base URL</label>
                    <input type="url" id="api-url-input" value="${currentUrl}" style="width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-glass); background: var(--bg-page); color: var(--text-primary); font-family: monospace;">
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 0.75rem;">
                    <button class="btn-secondary-custom" onclick="document.getElementById('api-url-input').value = 'http://127.0.0.1:8000'">Reset Local</button>
                    <button class="btn-primary-custom" onclick="UI.saveBackendUrl()">Save & Reload</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    },

    saveBackendUrl() {
        const input = document.getElementById('api-url-input');
        if (input && input.value) {
            CONFIG.setApiBaseUrl(input.value.trim());
            this.showToast('Backend API URL saved! Reloading...', 'success');
            setTimeout(() => window.location.reload(), 1000);
        }
    }
};

const AUTH = {
    async login(username, password) {
        try {
            const data = await API.post('/api/auth/login/', { username, password });
            API.setToken(data.token);
            API.setUser(data.user);
            UI.showToast(`Welcome back, ${data.user.name}!`, 'success');

            setTimeout(() => {
                if (data.user.role === 'admin') {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'student.html';
                }
            }, 600);
        } catch (err) {
            UI.showToast(err.message, 'error');
            throw err;
        }
    },

    async register(formData) {
        try {
            const data = await API.post('/api/auth/register/', formData);
            API.setToken(data.token);
            API.setUser(data.user);
            UI.showToast('Registration successful! Redirecting...', 'success');

            setTimeout(() => {
                window.location.href = 'student.html';
            }, 800);
        } catch (err) {
            UI.showToast(err.message, 'error');
            throw err;
        }
    },

    async logout() {
        try {
            await API.post('/api/auth/logout/');
        } catch (e) {
            // ignore network error on logout
        } finally {
            API.clearAuth();
            UI.showToast('Logged out successfully.', 'info');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 500);
        }
    },

    requireAuth(role = null) {
        const user = API.getUser();
        const token = API.getToken();

        if (!token || !user) {
            window.location.href = 'index.html';
            return null;
        }

        if (role && user.role !== role) {
            if (user.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'student.html';
            }
            return null;
        }

        return user;
    },

    redirectIfAuthenticated() {
        const user = API.getUser();
        const token = API.getToken();
        if (token && user) {
            if (user.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'student.html';
            }
        }
    }
};

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    UI.initTheme();
});
