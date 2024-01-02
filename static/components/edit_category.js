// Here, the edit_category.js component provides the interface for the modification and updation of an existing category.
const edit_category = {
    template: `
    <div class="center-box bg-white rounded">
        <div v-if="success">
            <h1>Edit Category</h1>
            <br>
            <form @submit.prevent="updateCategory">
                <div class="input-container">
                    <label for="name">Category Name:</label>
                    <input v-model="category.name" type="text" required />
                </div>
                <br>
                <div class="input-container">
                    <label for="description">Description:</label>
                    <input v-model="category.description" type="text" />
                </div>
                <br>
                <button type="submit" class="btn btn-outline-primary-2">Update</button>
            </form>
            <br>
            <button @click="goToViewCategories" class="btn btn-outline-primary">Go back to Categories</button>
        </div>
        <div v-else style="color: red">
        {{errorMessage}}
        <br><br>
        <button @click="goToViewCategories" class="btn btn-outline-primary">Go back to Categories</button>
        </div>
    </div>
    `,

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

    async mounted() {
        try {
            const res = await fetch(`/api/edit_category/${this.$route.params.id}`, {
                headers: {
                    'Authentication-Token': localStorage.getItem('auth-token')
                }
            });
            if (!res.ok) {
                this.success = false;
                this.errorMessage = await res.text();;
            }
            this.category = await res.json();

        } catch (error) {
            console.error("Error in mounted:", error);
            this.success = false;
            this.errorMessage = "An error occurred while fetching category details.";
        }
    },

    methods: {
        async updateCategory() {
            const response = await fetch(`/api/edit_category/${this.$route.params.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
                body: JSON.stringify(this.category)
            });
            if (!response.ok) {
                const data = await response.json();
                this.errorMessage = data.message;
                this.success = false;
                return;
            }
            alert('Category modified successfully!');
            this.$router.push('/view_categories');
        },
        goToViewCategories() {
            this.$router.push('/view_categories');
        },
    }
};


export default edit_category;