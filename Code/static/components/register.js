// Here, the register.js component provides the interface for the provision of a register form.
const register = {
    template: `
        <div class="center-box">
            <h2>Register</h2>
            <form @submit.prevent="registerUser">
            <br>
            <div class="input-container">
                <label for="formData.username">Username :  </label>
                <input v-model="formData.username" placeholder="Your Name">
            </div>
            <br>
            <div class="input-container">
                <label for="email">Email: </label>
                <input type="email" v-model="formData.email" placeholder="abc@gmail.com">
            </div>
            <br>
            <div class="input-container">
                <label for="password">Password :  </label>
                <input type="password" v-model="formData.password" placeholder="password@123">
            </div>
            <br>
            <div class="input-container">
                <label for="formData.role">Type of User :  </label>
                <select v-model="formData.role">
                    <option value="User">User</option>
                    <option value="Store Manager">Store Manager</option>
                </select>
            </div>
            <br>
            <div v-if="formData.role === 'Store Manager'">
                <p>Your account will be created post approval from the admin, till then you account is disabled.<br>
                Kindly wait for the approval on your registered email address.</p>
            </div>
            <br>
            <br>
                <button type="submit" class="btn custom-btn-submit">Register</button>
                <p v-if="error" style="color: red">{{ error }}</p>
            </form>

            <br>
            <div class="mt-2 d-flex justify-content-center">
                <span>Already have an account? <router-link to="/login">Log In Now</router-link></span>
            </div>

            <br>
            <div class="mt-2 d-flex justify-content-center">
                <router-link to="/">Back</router-link>
            </div>
        </div>
    `,
    data() {
        return {
            formData: {
                username: '',
                email: '',
                password: '',
                role: 'User',
            },
            error: null,
            userId: 0,
        }
    },

    methods: {
        async registerUser() {
            try {
                const res = await fetch('/register_app', {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.formData),
                });

                if (!res.ok) {
                    const errorData = await res.json();
                    this.error = errorData.message;
                } else {
                    console.log("Registered Successfully!");
                    this.$router.push('/login');
                }
            } catch (error) {
                this.error = error.message;
                console.error('Error during registration:', error.message);
            }
        },
    },
}

// In the end, we export the component to be used in the enitre application
export default register;