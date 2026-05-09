/**
 * Main JavaScript file for Knowledge Hub Monitoring Frontend
 */

// Configuration
const API_CONFIG = {
    base_url: '/api/web',
    refresh_interval: 30000, // 30 seconds
    timeout: 10000
};

// Auto-refresh utilities
class RefreshManager {
    constructor(interval = API_CONFIG.refresh_interval) {
        this.interval = interval;
        this.timer = null;
        this.isEnabled = true;
    }

    start(callback) {
        if (this.isEnabled) {
            this.timer = setInterval(callback, this.interval);
        }
    }

    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    resume() {
        this.isEnabled = true;
    }

    pause() {
        this.isEnabled = false;
        this.stop();
    }
}

// API utilities
class APIManager {
    static async fetch(endpoint, options = {}) {
        const url = `${API_CONFIG.base_url}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    static async getMetrics(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.fetch(`/metrics?${params}`);
    }

    static async getMetricsSummary() {
        return this.fetch('/metrics/summary');
    }

    static async getStatus() {
        return this.fetch('/status');
    }
}

// Utility functions
function formatTimestamp(isoString, format = 'short') {
    if (!isoString) return 'N/A';

    try {
        const date = new Date(isoString);
        if (format === 'short') {
            return date.toLocaleTimeString();
        } else if (format === 'full') {
            return date.toLocaleString();
        }
        return isoString;
    } catch (error) {
        console.warn('Invalid timestamp:', isoString);
        return isoString;
    }
}

function formatMetricValue(value, precision = 2) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
        return value.toFixed(precision);
    }
    return value;
}

function getStatusBadgeClass(status) {
    const statusMap = {
        'ok': 'success',
        'healthy': 'success',
        'warning': 'warning',
        'degraded': 'warning',
        'critical': 'danger',
        'down': 'danger'
    };
    return statusMap[status.toLowerCase()] || 'secondary';
}

// DOM utilities
function showAlert(message, type = 'info', dismissible = true) {
    const alertId = `alert-${Date.now()}`;
    const dismissBtn = dismissible ? `<button type="button" class="btn-close" data-bs-dismiss="alert"></button>` : '';

    const alert = document.createElement('div');
    alert.id = alertId;
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `${message}${dismissBtn}`;

    const container = document.querySelector('main .container-fluid');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        if (!dismissible) {
            setTimeout(() => alert.remove(), 5000);
        }
    }
}

function showError(message) {
    showAlert(`<strong>Error!</strong> ${message}`, 'danger');
}

function showSuccess(message) {
    showAlert(`<strong>Success!</strong> ${message}`, 'success');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap tooltips are used
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+R to refresh (but allow browser default)
        // Ctrl+/ for help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showAlert('<strong>Keyboard Shortcuts:</strong><br>F5 - Refresh page<br>Ctrl+/ - This help', 'info', true);
        }
    });

    // Log page load time
    if (window.performance && window.performance.timing) {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page loaded in ${pageLoadTime}ms`);
    }
});

// Export for use in other scripts
window.MonitoringUI = {
    APIManager,
    RefreshManager,
    formatTimestamp,
    formatMetricValue,
    getStatusBadgeClass,
    showAlert,
    showError,
    showSuccess
};

console.log('Monitoring UI loaded successfully');
