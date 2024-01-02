// This is the view_products.js component which provides an interface to view and manage all the products.
const view_products = {
    template: `
    <div >
    <div v-if="success" class="center-box bg-white rounded">
        <h2 class="text-center">List of All Products</h2>

        <table class="cart-table">
            <thead>
                <tr>
                    <td><strong>S.No</strong></td>
                    <td><strong>Name</strong></td>
                    <td><strong>Manufacturing Date</strong></td>
                    <td><strong>Expiry Date</strong></td>
                    <td><strong>Price</strong></td>
                    <td><strong>Unit</strong></td>
                    <td><strong>Quantity Available</strong></td>
                    <td><strong>Description</strong></td>
                    <td><strong>Category</strong></td>
                    <td><strong>Edit</strong></td>
                    <td><strong>Delete</strong></td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(product,index) in products">
                    <td>{{ index+1 }}</td>
                    <td>{{ product.name }}</td>
                    <td>{{ product.manufacture_date }}</td>
                    <td>{{ product.expiry_date }}</td>
                    <td>{{ product.price }}</td>
                    <td>{{ product.unit }}</td>
                    <td>{{ product.quantity_available }}</td>
                    <td>{{ product.description }}</td>
                    <td>
                        <p v-for="category in cats" v-if="product.category_product === category.id">
                            {{ category.name }}
                        </p>
                    </td>


                    
                    <td><button @click="edit_prod(product.id)" class="edit-button">Edit</button></td>
                    <td><button @click="delete_prod(product.id)" class="delete-button">Delete</button></td>
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
            products: [],
            cats: [],
            success: true,
            error: '',
            userId: localStorage.getItem('userId')
        };
    },


    async mounted() {
        const response = await fetch('/api/view_products', {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (response.ok) {
            this.products = await response.json();
        } else {
            this.success = false
            this.error = 'Failed to fetch products.';
        }

        const catResponse = await fetch('/api/view_categories', {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (catResponse.ok) {
            this.cats = await catResponse.json();
        } else {
            this.success = false
            this.error = ' Failed to fetch categories.';
        }
    },

    methods: {
        edit_prod(productId) {
            this.$router.push(`/edit_product/${productId}`);
        },
        delete_prod(productId) {
            this.$router.push(`/delete_product/${productId}`)
        },
        goToStoreManagerDashboard() {
            this.$router.push('/store_manager_dashboard')
        },

    }
};

export default view_products;