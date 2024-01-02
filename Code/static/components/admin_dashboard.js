// Here, the admin_dashboard.js component provides the interface for the admin's dashboard.
const admin_dashboard = {
    template: `
    <div>
    <div v-if="success" id="app" class="center-box bg-white rounded">
        <h2>Category Management</h2>
        <ul>
        <div class="container mt-5">
            <router-link to="/create_category" class="btn btn-link-custom">Create a New Category</router-link><br>
            <router-link to="/view_categories" class="btn btn-link-custom">View/Modify All Categories</router-link>
        </div>
        </ul>

        <h3 v-if="inactiveUsers.length">Inactive Store Manager Requests</h3>
        <table class="cart-table" v-if="inactiveUsers.length">
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="user in inactiveUsers">
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                        <button class="btn btn-outline-primary-2" @click="approveUser(user.id)">Approve</button>
                        <button class="btn btn-outline-danger" @click="declineUser(user.id)">Decline</button>
                    </td>
                </tr>
            </tbody>
        </table>
        <br>
            

        <button @click="goToProfile" class="btn btn-outline-primary">Return to Profile Page</button>
        <button @click="goToPendingRequests" class="btn btn-outline-primary">Go to Pending Requests</button>
        <button @click="goToSettings" class="btn btn-outline-primary">Go to Admin Settings</button>
    </div>
    <div v-else style="color: red">
        {{error}}
    </div>
    </div>`,

    data() {
        return {
            userId: localStorage.getItem('userId'),
            success: true,
            inactiveUsers: []
        }

    },

    async mounted() {
        const inactiveRes = await fetch(`/api/inactive_users`, {
            headers: {
                'Authentication-Token': localStorage.getItem('auth-token')
            }
        });

        if (inactiveRes.ok) {
            this.inactiveUsers = await inactiveRes.json();
        } else {
            console.log("Failed to fetch inactive users.");
        }
    },

    methods: {
        async approveUser(Id) { // This method approves a store manager by setting their status to active.
            const res = await fetch(`/api/modify_inactive_users/${Id}`, {
                method: 'PUT',
                headers: {
                    'Authentication-Token': localStorage.getItem('auth-token')
                }
            });

            if (res.ok) {
                this.inactiveUsers = this.inactiveUsers.filter(user => user.id !== Id);
            } else {
                console.log("Failed to approve user.");
            }
        },

        async declineUser(Id) { // This method declines a store manager by removing their record from the database.
            const res = await fetch(`/api/modify_inactive_users/${Id}`, {
                method: 'DELETE',
                headers: {
                    'Authentication-Token': localStorage.getItem('auth-token')
                }
            });

            if (res.ok) {
                this.inactiveUsers = this.inactiveUsers.filter(user => user.id !== Id);
            } else {
                console.log("Failed to decline user.");
            }
        },

        goToProfile() {
            this.$router.push(`/profile/${this.userId}`);
        },
        goToPendingRequests() {
            this.$router.push(`/view_pending_requests`);
        },
        goToSettings() {
            this.$router.push('/admin_settings');
        }
    }
}

export default admin_dashboard;