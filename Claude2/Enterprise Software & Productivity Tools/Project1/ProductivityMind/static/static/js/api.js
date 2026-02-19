/**
 * ProductivityMind - API Client
 * Handles all HTTP requests to the backend API
 */

class APIClient {
    constructor() {
        this.baseURL = '';
        this.defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
    }

    /**
     * Make an HTTP request
     */
    async request(endpoint, options = {}) {
        const url = this.baseURL + endpoint;
        const config = { ...this.defaultOptions, ...options };

        try {
            const response = await fetch(url, config);

            // Check if response is HTML (error page) instead of JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Server returned non-JSON response:', text.substring(0, 200));
                throw new Error(`Server error (${response.status}): Please check the server logs`);
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Request failed with status ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// API endpoints organized by resource
const API = {
    client: new APIClient(),

    // Dashboard
    dashboard: {
        getData: () => API.client.get('/api/dashboard/'),
        getTrends: (days = 30) => API.client.get('/api/analytics/trends/', { days }),
    },

    // Tasks
    tasks: {
        list: (params = {}) => API.client.get('/api/tasks/', params),
        get: (id) => API.client.get(`/api/tasks/${id}/`),
        create: (data) => API.client.post('/api/tasks/create/', data),
        update: (id, data) => API.client.put(`/api/tasks/${id}/update/`, data),
        delete: (id) => API.client.delete(`/api/tasks/${id}/delete/`),
        bulkUpdateStatus: (taskIds, status) =>
            API.client.post('/api/tasks/bulk-status/', { task_ids: taskIds, status }),
    },

    // Projects
    projects: {
        list: () => API.client.get('/api/projects/'),
        get: (id) => API.client.get(`/api/projects/${id}/`),
        create: (data) => API.client.post('/api/projects/create/', data),
    },

    // Categories & Tags
    categories: {
        list: () => API.client.get('/api/categories/'),
    },

    tags: {
        list: () => API.client.get('/api/tags/'),
    },

    // Reports
    reports: {
        getSummary: (days = 30) =>
            API.client.get('/api/reports/summary/', { days }),
    },

    // AI Engine
    ai: {
        recalculate: () => API.client.post('/api/ai/recalculate/'),
        getRiskAssessment: (minRisk = 'high') =>
            API.client.get('/api/ai/risk-assessment/', { min_risk: minRisk }),
    },

    // Work Logs
    workLogs: {
        list: (params = {}) => API.client.get('/api/work-logs/', params),
        create: (data) => API.client.post('/api/work-logs/create/', data),
    },

    // Users
    users: {
        list: () => API.client.get('/api/users/'),
        getStats: (userId) => API.client.get(`/api/analytics/user/${userId}/`),
        getMyStats: () => API.client.get('/api/analytics/user/me/'),
    },
};

// Export for use in other files
window.API = API;
