/**
 * API Helper — Shared utilities for making authenticated API requests
 */
const API_BASE = window.location.origin;

async function apiRequest(url, method = 'GET', body = null, isFormData = false) {
    const token = localStorage.getItem('token');
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!isFormData && body) {
        headers['Content-Type'] = 'application/json';
    }

    const options = { method, headers };

    if (body) {
        options.body = isFormData ? body : JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${url}`, options);

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = '/';
        return null;
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function requireAuth(requiredRole = null) {
    const token = localStorage.getItem('token');
    const user = getUser();

    if (!token || !user) {
        window.location.href = '/';
        return false;
    }

    if (requiredRole && user.role !== requiredRole) {
        window.location.href = '/';
        return false;
    }

    return true;
}

function logout() {
    localStorage.clear();
    window.location.href = '/';
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function statusBadge(status) {
    const labels = {
        pending: '⏳ Pending',
        match_found: '🔗 Match Found',
        closed: '✅ Closed',
    };
    return `<span class="badge badge-${status}">${labels[status] || status}</span>`;
}

function typeBadge(type) {
    const labels = { lost: '🔴 Lost', found: '🟢 Found' };
    return `<span class="badge badge-${type}">${labels[type] || type}</span>`;
}
