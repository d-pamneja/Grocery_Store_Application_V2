// Here, the my_orders.js component provides the interface for viewing your previous orders
const MyOrderHistoryComponent = {
    template: `
        <div id="app">
            <div class="center-content">
                <h1>Your Previous Orders</h1>
                <div class='order-container'>
                    <div v-for="order in orders" class="order-box">
                        <h2>Order ID: {{ order.order_id }}</h2>
                        <p><strong>Datetime</strong>: {{ order.timestamp }}</p>
                        <p><strong>Grand Total</strong>: {{ order.grand_total }}</p>
                        <ul>
                            <li v-for="item in order.order_items">
                                <strong>Product</strong>: {{ item.product_name }}<br>
                                <strong>Quantity</strong>: {{ item.quantity }}<br>
                                <strong>Price</strong>: {{ item.price_at_purchase }}<br>
                                <strong>Total</strong>: {{ item.total }}
                            </li>
                        </ul>
                    </div>
                </div>
                <div class="profile-buttons">
                    <button @click="goToStoreUserDashboard">Go to User Dashboard</button>
                </div>
            </div>
        </div>
        
    `,
    data() {
        return {
            orders: [],
            userId: localStorage.getItem('userId')
        };
    },
    async mounted() {

        const response = await fetch(`/api/my_orders/${this.userId}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            }
        });

        if (response.ok) {
            this.orders = await response.json();
        } else {
            console.error("Failed to fetch orders.");
        }
    },
    methods: {
        goToStoreUserDashboard() {
            this.$router.push('/user_dashboard')
        },
    }
};

export default MyOrderHistoryComponent;