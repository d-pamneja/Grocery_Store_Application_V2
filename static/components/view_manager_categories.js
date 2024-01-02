// This is the view_categories.js component which provides an interface to view and manage all the categories.
const view_manager_categories = {
    template: `
    <div>
    <div v-if="success" class="center-box bg-white rounded">
        <h2 class="text-center">List of All Categories Registered</h2>

        <table class="cart-table">
            <thead>
                <tr>
                    <th> S.No</th>
                    <th> Name</th>
                    <th> Description</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="category in categories">
                    <td>{{ category.id }}</td>
                    <td>{{ category.name }}</td>
                    <td>{{ category.description }}</td>
                    
                </tr>
            </tbody>
        </table>
        <br><br>
        <button @click="goToStoreManagerDashboard" class="btn btn-outline-primary">Go to Store Manager Dashboard</button>
    </div>
    <div v-else style="color: red">
    {{error}}
    <br><br>
    <button @click="goToStoreManagerDashboard" class="btn btn-outline-primary">Go to Store Manager Dashboard</button>
    </div>
    </div>
    `,

    data() {
        return {
            categories: [],
            success: true,
            error: '',
            userId: localStorage.getItem('userId')
        };
    },


    async mounted() {
        const response = await fetch('/api/view_categories', {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (response.ok) {
            this.categories = await response.json();
        } else {
            this.success = false
            this.error = 'Failed to fetch categories.';
        }
    },

    methods: {
        goToStoreManagerDashboard() {
            this.$router.push('/store_manager_dashboard')
        },

    }
};

export default view_manager_categories;