// Here, the create_category.js component provides the interface for the creation of a new category.
const create_category = {
    template: `
    <div class="center-box bg-white rounded">
        <div v-if="success"> 
            <h1>Add a Category</h1>
            <br>
            <form @submit.prevent="createCategory">
            <div class="input-container">
                <label for="name">Enter the Category Name:</label>
                <input v-model="category.name" type="text" id="name" required />
            </div>
            <br>
            <div class="input-container">
                <label for="description">Enter a short description of Category (optional):</label>
                <input v-model="category.description" type="text" id="description" />
            </div>
            <br>
            <button type="submit" class="btn btn-outline-primary-2">Add Category</button>
            <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
            </form>
            <br>
            <button @click="goToAdminDashboard" class="btn btn-outline-primary">Go back to Admin Dashboard</button>
        </div>
        <div v-else style="color: red">
            {{errorMessage}}
            <br><br>
            <button @click="goToAdminDashboard" class="btn btn-outline-primary">Go back to Admin Dashboard</button>
        </div>
  </div>`,

    data() {
        return {
            category: {
                name: '',
                description: '',
            },
            errorMessage: '',
            success: true,
            userId: localStorage.getItem('userId')
        }
    },

    methods: {
        async createCategory() {
            try {
                const response = await fetch('/api/create_category', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': localStorage.getItem('auth-token')
                    },
                    body: JSON.stringify(this.category)
                });

                if (!response.ok) {
                    const data = await response.json();
                    this.errorMessage = data.message;
                    return;
                }

                alert('Category created successfully!');
                this.$router.push('/admin_dashboard');
            } catch (error) {
                this.success = false
                this.errorMessage = "Failed to create category!"
            }
        },
        goToAdminDashboard() {
            this.$router.push('/admin_dashboard');
        },
    },
}

export default create_category;