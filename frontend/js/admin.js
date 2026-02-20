/**
 * Admin Dashboard — Real-time reports, AI matches, filtering
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth('admin')) return;
});

function createAdminApp() {
    return {
        user: getUser(),
        activeTab: 'reports',
        reports: [],
        matches: [],
        loading: false,
        ws: null,
        newReportIds: new Set(),
        wsReconnectAttempts: 0,
        wsReconnectTimer: null,

        // Filters
        sectionFilter: '',
        timeFilter: '',
        statusFilter: '',
        typeFilter: '',

        // Mobile sidebar
        sidebarOpen: false,

        init() {
            this.loadReports();
            this.loadMatches();
            this.connectWebSocket();
        },

        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/admin`;

            try {
                this.ws = new WebSocket(wsUrl);
            } catch (e) {
                console.error('WebSocket creation failed:', e);
                this.scheduleReconnect();
                return;
            }

            this.ws.onopen = () => {
                console.log('🟢 WebSocket connected');
                this.wsReconnectAttempts = 0; // Reset on successful connection
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.event === 'new_report') {
                        // Add to reports list with animation flag
                        this.newReportIds.add(data.report.id);
                        this.reports.unshift(data.report);

                        // Remove animation flag after 3s
                        setTimeout(() => {
                            this.newReportIds.delete(data.report.id);
                        }, 3000);

                        // Reload matches if high matches found
                        if (data.high_matches > 0) {
                            this.loadMatches();
                        }
                    }
                } catch (e) {
                    console.error('WS parse error:', e);
                }
            };

            this.ws.onclose = () => {
                console.log('🔴 WebSocket disconnected');
                this.scheduleReconnect();
            };

            this.ws.onerror = () => {
                this.ws.close();
            };
        },

        scheduleReconnect() {
            const maxAttempts = 10;
            if (this.wsReconnectAttempts >= maxAttempts) {
                console.warn('Max WebSocket reconnect attempts reached. Stopping.');
                return;
            }
            // Exponential backoff: 1s, 2s, 4s, 8s... capped at 30s
            const delay = Math.min(1000 * Math.pow(2, this.wsReconnectAttempts), 30000);
            this.wsReconnectAttempts++;
            console.log(`Reconnecting WebSocket in ${delay / 1000}s (attempt ${this.wsReconnectAttempts}/${maxAttempts})...`);
            if (this.wsReconnectTimer) clearTimeout(this.wsReconnectTimer);
            this.wsReconnectTimer = setTimeout(() => this.connectWebSocket(), delay);
        },

        async loadReports() {
            this.loading = true;
            try {
                const params = new URLSearchParams();
                if (this.sectionFilter) params.append('section', this.sectionFilter);
                if (this.timeFilter) params.append('time_filter', this.timeFilter);
                if (this.statusFilter) params.append('status', this.statusFilter);
                if (this.typeFilter) params.append('report_type', this.typeFilter);

                const qs = params.toString();
                this.reports = await apiRequest(`/api/admin/reports${qs ? '?' + qs : ''}`);
            } catch (err) {
                console.error('Failed to load reports:', err);
            } finally {
                this.loading = false;
            }
        },

        async loadMatches() {
            try {
                this.matches = await apiRequest('/api/admin/matches');
            } catch (err) {
                console.error('Failed to load matches:', err);
            }
        },

        async updateStatus(reportId, newStatus) {
            try {
                await apiRequest(`/api/admin/reports/${reportId}/status`, 'PATCH', { status: newStatus });
                // Update local state
                const report = this.reports.find(r => r.id === reportId);
                if (report) report.status = newStatus;
            } catch (err) {
                alert(err.message || 'Failed to update status');
            }
        },

        applyFilter(type, value) {
            if (type === 'section') {
                this.sectionFilter = this.sectionFilter === value ? '' : value;
            } else if (type === 'time') {
                this.timeFilter = this.timeFilter === value ? '' : value;
            } else if (type === 'status') {
                this.statusFilter = this.statusFilter === value ? '' : value;
            } else if (type === 'type') {
                this.typeFilter = this.typeFilter === value ? '' : value;
            }
            this.loadReports();
        },

        clearFilters() {
            this.sectionFilter = '';
            this.timeFilter = '';
            this.statusFilter = '';
            this.typeFilter = '';
            this.loadReports();
        },

        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },

        isNewReport(id) {
            return this.newReportIds.has(id);
        },

        get stats() {
            return {
                total: this.reports.length,
                pending: this.reports.filter(r => r.status === 'pending').length,
                matched: this.reports.filter(r => r.status === 'match_found').length,
                closed: this.reports.filter(r => r.status === 'closed').length,
                lost: this.reports.filter(r => r.type === 'lost').length,
                found: this.reports.filter(r => r.type === 'found').length,
            };
        },

        scoreColor(score) {
            if (score >= 0.7) return 'var(--success)';
            if (score >= 0.4) return 'var(--warning)';
            return 'var(--text-muted)';
        },

        scorePercent(score) {
            return Math.round(score * 100);
        },
    };
}
