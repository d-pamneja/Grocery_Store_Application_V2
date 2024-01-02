// Here, the store_manager_dashboard.js component provides the interface for the store manager's dashboard.
const store_manager_dashboard = {
    template: `
    <div>
    <div v-if="success" id="app" class="center-box bg-white rounded">
        <h2>Product Management</h2>
        <ul>
        <div class="container mt-5">
            <router-link to="/create_product" class="btn btn-link-custom">Create a New Product</router-link><br>
            <router-link to="/view_products" class="btn btn-link-custom">View/Modify Existing Products</router-link><br>
            <router-link to="/view_manager_categories" class="btn btn-link-custom">View All Available Categories</router-link>
        </div>
        </ul>
            
        <button @click="goToProfile" class="btn btn-outline-primary">Return to Profile Page</button>
        <button @click="submitRequesttoAdmin" class="btn btn-outline-primary">Request the Admin</button>
        <button @click="trigger_product_csv_celery" class="btn btn-outline-primary">Generate Product Report</button>
    </div>
    <div v-else style="color: red">
        {{error}}
    </div>
    </div>`,

    data() {
        return {
            userId: localStorage.getItem('userId'),
            email: localStorage.getItem('email'),
            success: true,
        }

    },

    methods: {
        goToProfile() {
            this.$router.push(`/profile/${this.userId}`);
        },
        submitRequesttoAdmin() {
            this.$router.push('/category_requests');
        },
        trigger_product_csv_celery() {
            fetch('/generate_csv/' + this.userId + '/' + this.email, { method: 'get' })
            alert("File generated successfully and sent to registered email.")
        }
    },
}


export default store_manager_dashboard;