// Here, the delete_category.js component provides the interface for the deletion of an existing category.
const delete_category = {
    template: `
    <div class="center-box bg-white rounded">
        <div v-if="success">
            <h1 style="color: red">Are you sure you want to delete this category?</h1>
            <br>
            <p style="color: black">This cannot be undone. All the products in this category will be deleted as well.</p>
            <br>
            <button @click="confirmDelete" class = "btn btn-outline-danger">Confirm Delete</button>
            <br>
            <br>
            <button @click="goToViewCategories" class="btn btn-outline-primary">Go back to Categories</button>
        </div>
        <div v-else style="color: red">
            {{errorMessage}}
            <br>
            <br>
            <button @click="goToViewCategories" class="btn btn-outline-primary">Go back to Categories</button>
        </div>
    </div>
    `,

    data() {
        return {
            errorMessage: '',
            success: true,
            userId: localStorage.getItem('userId')
        };
    },

    methods: {
        async confirmDelete() {
            try {
                const response = await fetch(`/api/delete_category/${this.$route.params.id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authentication-Token': localStorage.getItem('auth-token')
                    }
                });

                if (!response.ok) {
                    success = false
                    throw new Error(await response.text());
                }

                alert('Category deleted successfully!');
                this.$router.push('/view_categories');
            } catch (error) {
                console.error("Error during deletion:", error);
                this.errorMessage = "Failed to delete the category.";
            }
        },
        goToViewCategories() {
            this.$router.push('/view_categories');
        },
    },
    async mounted() {
        const res = await fetch(`/api/user_details`, {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (res.ok) {
            const userDetails = await res.json();
            this.userId = userDetails.id;
        } else {
            this.success = false
        }
    }
};

// In the end, we export the component to be used in the enitre application
export default delete_category;