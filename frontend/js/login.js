/**
 * Login Page Logic — Sliding panel between Student and Admin
 */
document.addEventListener('DOMContentLoaded', () => {
    // If already logged in, redirect
    const user = getUser();
    if (user) {
        window.location.href = user.role === 'admin' ? '/admin' : '/student';
        return;
    }
});

function createLoginApp() {
    return {
        mode: 'student',
        username: '',
        password: '',
        error: '',
        loading: false,

        get isAdmin() {
            return this.mode === 'admin';
        },

        switchMode() {
            this.mode = this.mode === 'student' ? 'admin' : 'student';
            this.error = '';
            this.username = '';
            this.password = '';
        },

        async login() {
            this.error = '';
            if (!this.username.trim() || !this.password.trim()) {
                this.error = 'Please enter both username and password';
                return;
            }

            this.loading = true;
            try {
                const data = await apiRequest('/api/auth/login', 'POST', {
                    username: this.username.trim(),
                    password: this.password,
                });

                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));

                // Redirect based on role
                if (data.user.role === 'admin') {
                    window.location.href = '/admin';
                } else {
                    window.location.href = '/student';
                }
            } catch (err) {
                this.error = err.message || 'Invalid credentials';
            } finally {
                this.loading = false;
            }
        },
    };
}
