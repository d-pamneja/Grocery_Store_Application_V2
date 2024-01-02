// Here, the delete_product.js component provides the interface for the deletion of an existing product.
const delete_product = {
    template: `
    <div class="center-box bg-white rounded">
        <div v-if="success">
            <h1 style="color: red">Are you sure you want to delete this product?</h1>
            <p style="color: black">This cannot be undone.</p>
            <button @click="confirmDeleteProd" class = "btn btn-outline-danger">Confirm Delete</button>
            <br><br>
            <button @click="goToViewProducts" class = "btn btn-outline-primary">Go back to Products</button>
        </div>
        <div v-else style="color: red">
            {{errorMessage}}
            <br><br>
            <button @click="goToViewProducts" class = "btn btn-outline-primary">Go back to Products</button>
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
        async confirmDeleteProd() {
            try {
                const response = await fetch(`/api/delete_product/${this.$route.params.id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authentication-Token': localStorage.getItem('auth-token')
                    }
                });

                if (!response.ok) {
                    success = false
                    throw new Error(await response.text());
                }

                alert('Product deleted successfully!');
                this.$router.push('/view_products');
            } catch (error) {
                console.error("Error during deletion:", error);
                this.errorMessage = "Failed to delete the product.";
            }
        },
        goToViewProducts() {
            this.$router.push('/view_products');
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
            console.log("ERROR")
            this.success = false
        }
    }
};


export default delete_product;