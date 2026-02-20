/**
 * Student Dashboard — Chatbot-style interactive reporting
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth('student')) return;
});

const LOCATIONS = {
    'A Block': ['Floor 1', 'Floor 2', 'Floor 3', 'Floor 4'],
    'B Block': ['Floor 1', 'Floor 2'],
    'C Block': ['Floor 1', 'Floor 2', 'Floor 3'],
    'Canteen': ['Aryas', 'VVDN'],
    'CC Hall': [],
};

const CATEGORIES = [
    'Electronics', 'Books & Notes', 'ID Card', 'Keys',
    'Wallet / Purse', 'Clothing', 'Accessories', 'Water Bottle',
    'Bag / Backpack', 'Stationery', 'Other',
];

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];

function createStudentApp() {
    return {
        user: getUser(),
        step: 0,
        maxStep: 0,
        reportType: '',
        itemName: '',
        category: '',
        description: '',
        block: '',
        floor: '',
        specificLocation: '',
        dateReported: new Date().toISOString().slice(0, 10),
        imageFile: null,
        imagePreview: '',
        submitting: false,
        showSuccess: false,
        myReports: [],
        loadingReports: false,
        categories: CATEGORIES,
        locations: LOCATIONS,

        get availableFloors() {
            return this.block ? (LOCATIONS[this.block] || []) : [];
        },

        get blockNames() {
            return Object.keys(LOCATIONS);
        },

        init() {
            this.loadMyReports();
        },

        selectType(type) {
            this.reportType = type;
            this.nextStep();
        },

        nextStep() {
            this.step++;
            if (this.step > this.maxStep) this.maxStep = this.step;
            this.$nextTick(() => {
                const el = document.querySelector(`[data-step="${this.step}"]`);
                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        },

        prevStep() {
            if (this.step > 0) this.step--;
        },

        onBlockChange() {
            this.floor = '';
        },

        handleImageSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Validate file type
            if (!ALLOWED_TYPES.includes(file.type)) {
                alert('Please select an image file (JPEG, PNG, GIF, WebP, or BMP)');
                event.target.value = '';
                return;
            }

            // Validate file size
            if (file.size > MAX_FILE_SIZE) {
                alert(`File is too large. Maximum size is ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
                event.target.value = '';
                return;
            }

            this.imageFile = file;
            const reader = new FileReader();
            reader.onload = (e) => { this.imagePreview = e.target.result; };
            reader.readAsDataURL(file);
        },

        async submitReport() {
            if (this.submitting) return;
            this.submitting = true;

            try {
                const formData = new FormData();
                formData.append('type', this.reportType);
                formData.append('item_name', this.itemName);
                formData.append('category', this.category);
                formData.append('description', this.description);
                formData.append('block', this.block);
                formData.append('floor', this.floor);
                formData.append('specific_location', this.specificLocation);
                formData.append('date_reported', this.dateReported);
                if (this.imageFile) {
                    formData.append('image', this.imageFile);
                }

                await apiRequest('/api/reports', 'POST', formData, true);
                this.showSuccess = true;

                setTimeout(() => {
                    this.showSuccess = false;
                    this.resetForm();
                    this.loadMyReports();
                }, 2500);
            } catch (err) {
                alert(err.message || 'Submission failed');
            } finally {
                this.submitting = false;
            }
        },

        resetForm() {
            this.step = 0;
            this.maxStep = 0;
            this.reportType = '';
            this.itemName = '';
            this.category = '';
            this.description = '';
            this.block = '';
            this.floor = '';
            this.specificLocation = '';
            this.dateReported = new Date().toISOString().slice(0, 10);
            this.imageFile = null;
            this.imagePreview = '';
        },

        async loadMyReports() {
            this.loadingReports = true;
            try {
                this.myReports = await apiRequest('/api/reports/my');
            } catch (err) {
                console.error('Failed to load reports:', err);
            } finally {
                this.loadingReports = false;
            }
        },
    };
}
