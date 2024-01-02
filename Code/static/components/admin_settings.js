// Here, the admin_settings.js component provides the interface for the admin's to view/modify the admin settings for monthly report.
const AdminSettings = {
    template: `
    <div class="center-box bg-white rounded">
        <h1>Admin Settings</h1>
        <br>
        <form @submit.prevent="updateReportFormat">
            <label>Report Format:</label>
            <label>
                <select v-model="selectedFormat">
                    <option value="html">Email</option>
                    <option value="pdf">PDF</option>
                </select>
            </label>
            <br>
            <button type="submit" class="btn btn-outline-primary-2">Submit</button>
        </form>
        <br>
        <button @click="goToAdminDashboard" class="btn btn-outline-primary">Go back to Admin Dashboard</button>
    </div>
    `,
    data() {
        return {
            selectedFormat: 'html',
        };
    },
    created() {
        this.fetchAdminSettings();
    },
    methods: {
        async fetchAdminSettings() {
            const response = await fetch('/api/update_report_format', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token'),
                },
            });

            if (response.ok) {
                const settings = await response.json();
                this.selectedFormat = settings.report_format;
            } else {
                alert('Failed to fetch admin settings.');
            }
        },
        async updateReportFormat() {
            const response = await fetch('/api/update_report_format', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
                body: JSON.stringify({ format: this.selectedFormat }),
            });

            if (response.ok) {
                alert('Report format updated successfully!');
                this.goToAdminDashboard();
            } else {
                alert('Failed to update report format.');
            }
        },
        goToAdminDashboard() {
            this.$router.push('/admin_dashboard');
        }
    },
};

export default AdminSettings;