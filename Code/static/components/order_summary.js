// Here, the order_summary.js component provides the interface for to view the latest order, usually immediately after the purchase is successful
const orderSummaryComponent = {
    template: `
        <div v-if="order" class="center-content">
            <h3>Order Summary</h3>
            <table class="cart-table">
                <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Item Total</th>
                </tr>

                <tr v-for="item in order.order_items">
                    <td>{{ item.product_name }}</td>
                    <td>{{ item.price_at_purchase }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.total }}</td>
                </tr>
            </table>
            <h2 style="text-align:center; margin-top: 20px;">Grand Total: {{ order.grand_total }}</h2>
            <div class="profile-buttons">
                <button @click="goToUserDashboard">Go back to User Dashboard</button>
            </div>
        </div>
        <div v-else>
            <h2>Failed to fetch order details.</h2>
        </div>
    `,
    data() {
        return {
            order: [],
            userId: localStorage.getItem('userId')
        };
    },
    async mounted() {

        try {
            const response = await fetch(`/api/get_latest_order/${this.userId}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token')
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Received data:", data);
                this.order = data;
            } else {
                console.error("Failed to fetch order details:", await response.text());
            }
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    },
    methods: {
        goToUserDashboard() {
            this.$router.push('/user_dashboard')
        },
    }

}


export default orderSummaryComponent;