// Here, the view_cart.js component provides the interface for viewing the cart
const cartComponent = {
    template: `
    <div v-if="success" id="app" >
        <div v-if="items.length > 0" class="center-content">
            <h2><strong><u>Cart</u></strong></h2>
            <table class="cart-table">
                <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Item Total</th>
                    <th>Edit</th>
                    <th>Delete</th>
                </tr>

                <tr v-for="item in items">
                    <td>{{ getProductName(item.product_id) }}</td>
                    <td>{{ getProductPrice(item.product_id) }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ computeItemTotal(item) }}</td>
                    <td><button class="edit-button" @click="editItem(item)">Edit</button></td>
                    <td><button class="delete-button" @click="deleteItem(item)">Delete</button></td>
                </tr>
            </table>

            <br><br><br>
            <div class="discount-section">
                <input type="text" v-model="discountCode" placeholder="Enter discount code" />
                <button @click="applyDiscount">Apply Discount</button>
                <br><br>
                <strong>Available Discounts:</strong>
                    <li>WELCOME10 - A welcoming bonus of 10% off on the total bill. Note that this applies to first orders ONLY.</li>
                <div v-if="isDiscounted">
                    <br>
                    <strong>Discount Applied:</strong> {{ discountAmount }}
                </div>
            </div>

            <br><br>
            <div class="total-section">
                <strong>Total:</strong> {{ items.reduce((sum, item) => sum + computeItemTotal(item), 0) - discountAmount }}
            </div>

            <br><br>
            <div class="confirm-order-section">
                <button @click="buyNow">Confirm Order</button>
            </div>

            <div class="profile-buttons">
                <button @click="goToUserDashboard">Go back to User Dashboard</button>
            </div>
        </div>
        <div v-else class="profile-container">
            <h4>Your cart is empty. Start shopping!</h4>
            <div class="profile-buttons">
            <button @click="goToUserDashboard">Go back to User Dashboard</button>
        </div>
        </div>

        
    </div>
    <div v-else-if="orderSummary" class="center-content">
        <h3>Order Summary</h3>
        <table>
            <!-- Table Headers -->
            <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Item Total</th>
            </tr>

            <tr v-for="item in orderSummary.order_items">
                <td>{{ item.product_name }}</td>
                <td>{{ item.price_at_purchase }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.total }}</td>
            </tr>
        </table>
        <h2 style="text-align:center; margin-top: 20px;">Grand Total: {{ orderSummary.grand_total }}</h2>
        <br>

        <button @click="goToUserDashboard">Go back to User Dashboard</button>
    </div>
    `,
    data() {
        return {
            items: [],
            products: [],
            isDiscounted: false,
            discountAmount: 0,
            discountCode: '',
            totalAmount: 0,
            success: true,
            userId: localStorage.getItem('userId'),
            newproductdataToSend: {
                cart_item_id: null,
                product_id: null,
                quantity: null,
            },
            orderSummary: null
        }
    },
    methods: {
        goToUserDashboard() {
            this.$router.push('/user_dashboard')
        },
        computeItemTotal(item) {
            return this.getProductPrice(item.product_id) * item.quantity;
        },
        getProductName(productId) {
            const product = this.products.find(p => p.id === productId);
            return product ? product.name : 'Unknown Product';
        },
        getProductPrice(productId) {
            const product = this.products.find(p => p.id === productId);
            return product ? product.price : 0;
        },
        getProductID(productId) {
            const product = this.products.find(p => p.id === productId);
            return product ? product.id : 0;
        },
        async calculateTotalAmount() {
            const response = await fetch(`/api/cart_view/${this.userId}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
            });

            if (response.ok) {
                this.items = await response.json();
            } else {
                this.success = false;
                this.error = 'Failed to fetch products.';
            }

            const response2 = await fetch('/api/view_products_user', {
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                },
            });

            if (response2.ok) {
                this.products = await response2.json();
            } else {
                this.success = false;
                this.error = 'Failed to fetch products.';
            }

            this.totalAmount = this.items.reduce((sum, item) => sum + this.computeItemTotal(item), 0) - this.discountAmount;
        },
        async editItem(item) {
            this.newproductdataToSend.cart_item_id = item.id;
            const userInput = prompt("How many units of this product would you like to add to your cart?", item.quantity);

            if (userInput === null) {
                return;
            }

            const newquantity = parseInt(userInput);

            if (isNaN(newquantity) || newquantity < 1) {
                alert("Please enter a valid quantity.");
                return;
            }

            this.newproductdataToSend.quantity = newquantity;
            this.newproductdataToSend.product_id = item.product_id;


            try {
                const response = await fetch(`/api/edit_item/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': localStorage.getItem('auth-token')
                    },
                    body: JSON.stringify(this.newproductdataToSend)
                });

                if (response.ok) {
                    const data = await response.json();
                    alert(data.message);

                    const index = this.items.findIndex(i => i.id === item.id);
                    if (index !== -1) {
                        this.items[index].quantity = this.newproductdataToSend.quantity;
                    }

                    await this.calculateTotalAmount();

                } else {
                    const errorData = await response.json();
                    console.log('Error Data:', errorData);
                    alert(errorData.message || 'Failed to edit cart item.');
                }
            } catch (error) {
                console.error("There was an error updating the item:", error);
            }
        },
        async deleteItem(item) {
            try {
                const response = await fetch(`/api/delete_item/${item.id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': localStorage.getItem('auth-token')
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    alert(data.message);

                    this.items = this.items.filter(i => i.id !== item.id);

                    await this.calculateTotalAmount();

                } else {
                    const errorData = await response.json();
                    console.log('Error Data:', errorData);
                    alert(typeof errorData === 'object' ? JSON.stringify(errorData) : errorData.message);
                }
            } catch (error) {
                console.error("There was an error deleting the item:", error);
            }
        },
        async applyDiscount() {
            try {
                const response = await fetch(`/api/check_discount/${this.userId}?discount_code=${encodeURIComponent(this.discountCode)}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': localStorage.getItem('auth-token')
                    }
                });

                if (!response.ok) {
                    console.error("Error response:", await response.text());
                    alert("Invalid Coupon Code. Try Again.");
                    throw new Error('Failed to apply discount');
                }

                const data = await response.json();


                if (data.discount && data.discount > 0) {

                    this.isDiscounted = true;
                    this.discountAmount = (this.totalAmount * data.discount) / 100;

                    alert('Discount applied!');
                } else if (data.discount === 0) {
                    alert('You have already used your welcome discount.');
                } else if (data.message) {
                    alert(data.message);
                } else {
                    alert('Discount code is invalid or does not apply.');
                }

            } catch (error) {
                console.error("There was an error fetching the discount:", error);
            }
        },
        async buyNow() {
            try {
                const response = await fetch(`/api/buy_now`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': localStorage.getItem('auth-token')
                    },
                    body: JSON.stringify({
                        totalAmount: this.totalAmount,
                        items: this.items
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    this.items = [];
                    alert(data.message);
                    this.orderSummary = data;
                    this.$router.push(`/get_latest_order/${this.userId}`);
                } else {
                    alert(data.message || 'Failed to place order.');
                }
            } catch (error) {
                console.error("There was an error placing the order:", error);
            }
        },
    },
    async mounted() {
        const response = await fetch(`/api/cart_view/${this.userId}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (response.ok) {
            this.items = await response.json();
        } else {
            this.success = false
            this.error = 'Failed to fetch products.';
        }

        const response2 = await fetch('/api/view_products_user', {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (response2.ok) {
            this.products = await response2.json();
        } else {
            this.success = false
            this.error = 'Failed to fetch products.';
        }

        this.totalAmount = this.items.reduce((sum, item) => sum + this.computeItemTotal(item), 0) - this.discountAmount;

    }
}

export default cartComponent;