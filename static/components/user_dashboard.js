// Here, the user_dashboard.js component provides the interface for the user page
const user_dashboard = {
    template: `
    <div>
        <div v-if="success">
            <div class="navbar">
                <form action="/products_search" method="GET" class="search-form"">
                    <input type="text" v-model="searchQuery" placeholder="Search Products..." @input="searchProducts">
                </form>
                <div class="nav-buttons-right">
                    <button @click="goToCart" title="Cart"><img src="../static/cart_icon.png" alt = "Cart" class="icon-img-2"></button>
                </div>
            </div>

            <div class="main-content">
                <div class="product-container">
                    <div class="product-box" v-for="product in products">
                        <div class="product-name"><u>{{ product.name }}</u></div>
                        <div>{{ product.description }}</div>
                        <div><strong>Price/Unit:</strong> {{ product.price }}/{{ product.unit }}</div>
                        <div><strong>Manufacturing Date:</strong> {{ product.manufacture_date }}</div>
                        <div><strong>Expiry Date:</strong> {{ product.expiry_date }}</div>
                        <div><strong>Category:</strong> 
                            <span v-for="category in categories" v-if="product.category_product === category.id">
                                {{ category.name }}
                            </span>
                        </div>
                        <div v-if="product.quantity_available < 1" class="out-of-stock-message">Out of Stock</div>
                        <div v-else> 
                            <button @click.prevent="addToCart(product)">Add to Cart</button>
                        </div>
                    </div>
                </div>
            
                <div class="filters">
                    <h3><strong>Filter Products</strong></h3>
                    <br>
                    <h4>By Price:</h4>
                    Min: <input type="number" v-model="minPrice"><br>
                    Max: <input type="number" v-model="maxPrice">

                    <br>
                    <br>

                    <h4>By Manufacturing Date:</h4>
                    From: <input type="date" v-model="minManufactureDate">
                    To: <input type="date" v-model="maxManufactureDate">

                    <br>
                    <br>

                    <h4>By Expiry Date:</h4>
                    From: <input type="date" v-model="minExpiryDate">
                    To: <input type="date" v-model="maxExpiryDate">

                    <br>
                    <br>

                    <h4>By Category:</h4>
                    <select v-model="selectedCategory">
                        <option value="">--Select Category--</option>
                        <option v-for="category in categories" :value="category.id">{{ category.name }}</option>
                    </select>
                    <br>
                    <br>

                    <button @click="applyFilters">Apply Filters</button>
                    <button @click="clearFilters">Clear All Filters</button>
                </div>
            </div>
            
        </div>
        
        <div v-else style="color: red">
            <div class="invalid-auth-page">
                {{error}}
            </div>
        </div>
        <div class="profile-buttons">
            <button @click="goToProfile">Return to Profile Page</button>
            <button @click="goToMyOrders">View My Orders</button>
        </div>
    
    </div>`,

    data() {
        return {
            userId: localStorage.getItem('userId'),
            success: true,
            error: '',
            products: [],
            categories: [],


            minPrice: null,
            maxPrice: null,
            minManufactureDate: null,
            maxManufactureDate: null,
            minExpiryDate: null,
            maxExpiryDate: null,
            selectedCategory: null,

            searchQuery: null,

            productdataToSend: {
                product_id: null,
                quantity: null,
                price: null
            }
        }
    },

    async mounted() {
        const response = await fetch('/api/view_products_user', {
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
            this.categories = await catResponse.json();
        } else {
            this.success = false
            this.error += ' Failed to fetch categories.';
        }
    },

    methods: {
        goToProfile() {
            this.$router.push(`/profile/${this.userId}`);
        },

        goToCart() {
            this.$router.push(`/view_cart/${this.userId}`);
        },

        goToMyOrders() {
            this.$router.push(`/my_orders/${this.userId}`);
        },

        async addToCart(product) {
            const userInput = prompt("How many units of this product would you like to add to your cart?", "1");

            if (userInput === null) {
                return;
            }

            const quantity = parseInt(userInput);

            if (isNaN(quantity) || quantity < 1) {
                alert("Please enter a valid quantity.");
                return;
            }

            this.productdataToSend.product_id = product.id;
            this.productdataToSend.quantity = quantity;
            this.productdataToSend.price = product.price;

            console.log(this.productdataToSend);


            const response = await fetch(`/api/add_product_to_cart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
                body: JSON.stringify(this.productdataToSend)
            });

            const data = await response.json();

            if (response.ok) {
                this.productdataToSend = data;
                alert("Product added successfully!");

            } else {
                const errorMessage = data.message || 'Failed to add product to cart';
                alert(errorMessage);
            }
        },

        async applyFilters() {
            const filterData = {
                min_price: this.minPrice,
                max_price: this.maxPrice,
                min_manufacture_date: this.minManufactureDate,
                max_manufacture_date: this.maxManufactureDate,
                min_expiry_date: this.minExpiryDate,
                max_expiry_date: this.maxExpiryDate,
                category_id: this.selectedCategory
            };

            const response = await fetch('/api/filtered_products', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
                body: JSON.stringify(filterData)
            });

            if (response.ok) {
                this.products = await response.json();
            } else {
                this.error = 'Failed to fetch filtered products.';
                this.success = false;
            }
        },

        async clearFilters() {
            this.minPrice = null;
            this.maxPrice = null;
            this.minManufactureDate = null;
            this.maxManufactureDate = null;
            this.minExpiryDate = null;
            this.maxExpiryDate = null;
            this.selectedCategory = null;
            const response = await fetch('/api/clear_filters', {
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
            });

            if (response.ok) {
                this.products = await response.json();
            } else {
                alert('Failed to clear filters.');
            }
        },

        async searchProducts() {
            const response = await fetch(`/api/products_search?search=${this.searchQuery}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
            });

            if (response.ok) {
                this.products = await response.json();
            } else {
                alert('Failed to fetch search results.');
            }
        },

    }
}

export default user_dashboard;