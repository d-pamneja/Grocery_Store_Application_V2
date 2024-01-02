// Here, the create_product.js component provides the interface for the creation of a new product.
const create_product = {
    template: `
    <div class="center-box bg-white rounded">
        <div> 
            <h1>Add a Product</h1>
            <br>
            <form @submit.prevent="createProduct">
            <div class="input-container">
                <label for="name">Enter the Product Name:</label>
                <input v-model="product.name" type="text" id="name" required />
            </div>
            <br>
            <div class="input-container">
                <label for="manufacture_date">Enter the Product Manufacturing Date:</label>
                <input v-model="product.manufacture_date" type="date" id="manufacture_date" />
            </div>
            <br>
            <div class="input-container">
                <label for="expiry_date">Enter the Product Expiry Date:</label>
                <input v-model="product.expiry_date" type="date" id="expiry_date" />
            </div>
            <br>
            <div class="input-container">
                <label for="price">Enter the Product Price (INR):</label>
                <input v-model="product.price" type = 'number' min = "0.00" steps = "0.001" required id="price" />
            </div>
            <br>
            <div class="input-container">
                <label for="quantity_available">Enter the Product Quantity Available:</label>
                <input v-model="product.quantity_available" type = 'number' min = "1" steps = "1" required id="quantity_available" />
            </div>
            <br>
            <div class="input-container">
                    <label for="unit">Enter the Unit of Product:</label>
                        <select v-model="product.unit" name="unit" id="unit">
                            <option value="Kilograms">Kilograms</option>
                            <option value="Liters">Liters</option>
                            <option value="Gallon">Gallon</option>
                            <option value="Grams">Grams</option>
                            <option value="Millilitter">Millilitter</option>
                            <option value = "Ounce">Ounce</option>
                            <option value = "Piece">Piece</option>
                            <option value = "Others/NA">Other/Not Applicable</option> 
                        </select>
            </div>
            <br>
            <div class="input-container">
                    <label for="category_id">Select Category of Your Product:</label>
                    <select v-model="product.category_id" name="category_id" id="category_id" >
                        <option v-for="one in cats" :value="one.id">{{ one.name }}</option>
                    </select>
            </div>
            <br>
            
            <div class="input-container">
                <label for="description">Enter a short description of Product (optional):</label>
                <input v-model="product.description" type="text" id="description" />
            </div>
            <br>
            <button type="submit" class="btn btn-outline-primary-2">Add Product</button>
            <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
            </form>
            <br>
            <button @click="goToStoreManagerDashboard" class="btn btn-outline-primary">Go back to Store Manager Dashboard</button>
        </div>
    </div>`,

    data() {
        return {
            product: {
                name: '',
                manufacture_date: '',
                expiry_date: '',
                price: '',
                quantity_available: '',
                unit: '',
                description: '',
                category_product: ''

            },
            errorMessage: '',
            success: true,
            cats: [],
            userId: localStorage.getItem('userId')
        }
    },

    methods: {
        async createProduct() {

            const response = await fetch('/api/create_product', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
                body: JSON.stringify(this.product)
            });

            if (!response.ok) {
                const data = await response.json();
                this.success = false;
                this.errorMessage = data.message;
                return;
            }

            alert('Product created successfully!');
            this.$router.push('/store_manager_dashboard');

        },
        goToStoreManagerDashboard() {
            this.$router.push('/store_manager_dashboard')
        },
        async fetchCategories() {
            try {
                const response = await fetch('/api/view_categories', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': localStorage.getItem('auth-token')
                    },
                });

                if (response.ok) {
                    this.cats = await response.json();
                } else {
                    this.success = false
                    this.error = 'Failed to fetch categories.';
                }
            } catch (error) {
                this.success = false
                console.error("An error occurred while fetching categories:", error);
            }
        },
    },

    async mounted() {
        this.fetchCategories();
    },
}


export default create_product;