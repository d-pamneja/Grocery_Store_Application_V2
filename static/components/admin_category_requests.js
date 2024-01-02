// Here, the admin_category_requests.js component provides the interface for the admin's to view the category requests.
const AdminDisplayRequests = {
    template: `
    <div class="center-box bg-white rounded">
        <div v-if="requests.length > 0" >
        <h2>Category Requests</h2>
            <table class="cart-table">
                <thead>
                    <tr>
                        <th>Action</th>
                        <th>Category Name</th>
                        <th>Description</th>
                        <th>New Name</th>
                        <th>New Description</th>
                        <th>Reason</th>
                        <th>Approve</th>
                        <th>Deny</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="request in requests">
                        <td>{{ request.action }}</td>
                        <td>{{ getCategoryName(request.selectedCategory) }}</td>
                        <td>{{ request.description }}</td>
                        <td v-if="request.action === 'edit'">{{ request.name }}</td>
                        <td v-else></td>
                        <td v-if="request.action === 'edit'">{{ request.description }}</td>
                        <td v-else></td>
                        <td>{{ request.reason }}</td>
                        <td><button @click="approveRequest(request.id)" class="btn btn-outline-primary-2">Approve</button></td>
                        <td><button @click="denyRequest(request.id)" class="btn btn-outline-danger">Deny</button></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <h4 v-else>No pending category requests.</h4>
        <br>
        <button @click="goToAdminDashboard" class="btn btn-outline-primary">Go back to Admin Dashboard</button>
    </div>

    `,
    data() {
        return {
            requests: [],
            categories: []
        }
    },

    async mounted() {
        const response = await fetch('/api/all_category_requests', {
            headers: {
                'Authentication-Token': localStorage.getItem('auth-token')
            }
        });

        if (response.ok) {
            this.requests = await response.json();
        } else {
            alert('Failed to fetch category requests.');
        }

        const response2 = await fetch('/api/view_categories', {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (response2.ok) {
            this.categories = await response2.json();
        } else {
            this.success = false
            this.error = 'Failed to fetch categories.';
        }
    },


    methods: {
        getCategoryName(categoryId) {
            const category = this.categories.find(cat => cat.id === categoryId);
            return category ? category.name : 'Unknown';
        },

        async approveRequest(id) {
            const request = this.requests.find(req => req.id === id);
            if (!request) {
                alert('Request not found.');
                return;
            }

            console.log('Action:', request.action);
            console.log('selectedCategory', request.selectedCategory)

            let method = 'PUT';
            let endpoint = `/api/category_requests/admit/${id}`;

            if (request.action === 'edit') {
                endpoint = `/api/category_requests/admit/edit/${id}/${request.selectedCategory}`;
            } else if (request.action === 'remove') {
                endpoint = `/api/category_requests/admit/delete/${id}/${request.selectedCategory}`;
                method = 'DELETE';
            }

            const response = await fetch(endpoint, {
                method: method,
                headers: {
                    'Authentication-Token': localStorage.getItem('auth-token')
                }
            });


            if (response.ok) {
                alert('Request approved successfully!');
                this.requests = this.requests.filter(req => req.id !== id);
            } else {
                alert('Failed to approve the request.');
            }
        },

        async denyRequest(id) {
            const response = await fetch(`/api/category_requests/deny/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authentication-Token': localStorage.getItem('auth-token')
                }
            });

            if (response.ok) {
                alert('Request denied.');
                this.requests = this.requests.filter(req => req.id !== id);
            } else {
                alert('Failed to deny the request.');
            }
        },
        goToAdminDashboard() {
            this.$router.push('/admin_dashboard');
        }
    }
};

export default AdminDisplayRequests;