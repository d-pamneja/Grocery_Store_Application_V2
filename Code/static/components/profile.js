// Here, the profile.js component provides the interface for the provision of the profile page, which is the landing page of a logged in user
const profile = {
    template: `
    <div>
        <div v-if="success">
            <div class="profile-container">
                <div class="user-info">
                <h1>Welcome to your Profile!!</h1>
                <p>Username: <strong>{{ profile.username }}</strong></p>
                <p>Email: <strong>{{ profile.email }}</strong></p>
                </div>

                <div class="nav-links">
                <button v-if="isAdmin" @click="goToAdminDashboard">Go to Admin Dashboard</button>
                <button v-if="isStoreManager" @click="goToStoreManagerDashboard">Go to Store Manager Dashboard</button>
                <button v-if="isUser" @click="goToStoreUserDashboard">Go to User Dashboard</button>
                </div>
            </div>
        </div>
        <div v-else style="color: red">
            {{ error }}
        </div>

        <div v-if="isAdmin" class="welcome-container">
            <h2>Welcome, {{ profile.username }}!</h2>
            <p>
            As the administrator of E-Bazaar, you play a crucial role in managing and overseeing the platform. Your responsibilities include:
            </p>
            
            <ul>
            <li>Creating and modifying categories under which products will be sold.</li>
            <li>Approving or denying registration requests from store managers.</li>
            <li>Reviewing and managing category requests from existing store managers.</li>
            <li>Receiving a monthly user-wise analysis report on purchase patterns, customizable to your preferred format.</li>
            </ul>

            <p>
            Feel free to explore the dashboard and take advantage of the powerful tools at your disposal. If you have any questions or need assistance, our support team is here to help. Thank you for your dedication to E-Bazaar's success!
            </p>
        </div>

        <div v-if="isStoreManager" class="welcome-container">
            <h2>Welcome, {{ profile.username }}!</h2>
            <p>
            Welcome to E-Bazaar! As a store manager, you play a vital role in curating and managing the products available on our platform. Your responsibilities include:
            </p>
            
            <ul>
            <li>Creating, modifying, and deleting products under categories made available by the admin.</li>
            <li>Requesting the admin to add, edit, or remove any category, along with providing a suitable reason for the request.</li>
            <li>Requesting a CSV file containing basic details and statistical information for all your products, which will be sent to your registered email address.</li>
            </ul>

            <p>
            Feel free to explore the product management dashboard and utilize the tools at your disposal. If you have any questions or need assistance, our support team is here to help. Thank you for your contribution to E-Bazaar's diverse product catalog!
            </p>
        </div>

        <div v-if="isUser" class="welcome-container">
            <h2>Welcome, {{ profile.username }}!</h2>
            <p>
            Welcome to E-Bazaar! We're thrilled to have you as part of our community. As a user, you have the power to explore, discover, and shop from a diverse range of products. Your journey includes:
            </p>
            
            <ul>
            <li>Browsing and searching for products based on name, category, manufacturer, expiry date, price range, and more.</li>
            <li>Adding products to your cart and seamlessly completing your purchase.</li>
            <li>Accessing your order history</li>
            <li>Enjoying a user-friendly experience designed to make your shopping journey delightful.</li>
            </ul>

            <p>
            Explore our product catalog, add your favorite items to the cart, and experience the joy of convenient online shopping. If you have any questions or need assistance, our support team is here to help. Thank you for choosing E-Bazaar — happy shopping!
            </p>
        </div>

        
    </div>
    `,

    data() {
        return {
            profile: {
                username: "Your User Name",
                email: "Your Email ID",
                role: "Role",
            },

            isAdmin: false,
            isStoreManager: false,
            isUser: false,
            success: true,
            error: "Something went wrong",
            userId: localStorage.getItem('userId')
        }
    },

    async mounted() {
        const res = await fetch(`http://127.0.0.1:5000/api/users/${this.userId}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        })
        const data = await res.json();
        localStorage.setItem('email', data.email);

        console.log(data)


        if (res.ok) {
            this.profile.username = data.username;
            this.profile.email = data.email;
            this.profile.role = data.role;
            if (this.profile.role == 'Admin') {
                this.isAdmin = true;
            }
            if (this.profile.role == 'Store Manager') {
                this.isStoreManager = true;
            }
            if (this.profile.role == 'User') {
                this.isUser = true;
            }

        } else if (res.status == 401) {
            this.success = false
            this.error = data.response.errors[0]

        } else {
            console.log("Something went wrong", res.statusText);
            this.success = false
            this.error = data.message
        }
    },

    methods: {
        goToAdminDashboard() {
            this.$router.push('/admin_dashboard');
        },
        goToStoreManagerDashboard() {
            this.$router.push('/store_manager_dashboard')
        },
        goToStoreUserDashboard() {
            this.$router.push('/user_dashboard')
        }
    },
}


export default profile;