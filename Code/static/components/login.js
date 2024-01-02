// Here, the login.js component provides the interface for the provision of a login form and logic for user authentication.
const login = {
    template: `
    <div class="center-box">
        <h1>Login</h1>
        <br>
        <form action="">
        <div class="input-container">
            <label for="email">Email: </label>
            <input type="text" name="email" id="email" placeholder="abc@gmail.com" v-model="formData.email" />
        </div>

        <br>
        <div class="input-container">
            <label for="password">Password:</label>
            <input type="password" name="password" placeholder="password@123" v-model="formData.password" />
        </div>

        <br>
        <button @click.prevent="loginUser" class="btn custom-btn-submit">Login</button>
        <p v-if="error" style="color: red">{{ error }}</p>
        </form>

        <div class="mt-2 d-flex justify-content-center">
            <span>Don't have an account? <router-link to="/register_app">Register Now</router-link></span>
        </div>

        <div class="mt-2 d-flex justify-content-center">
            <router-link to="/">Back</router-link>
        </div>
  </div>`,

    data() {
        return {
            formData: {
                email: '',
                password: '',
            },
            error: null,
            userId: 0
        }
    },


    methods: {
        async loginUser() {

            try {
                const res = await fetch('/login?include_auth_token', {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.formData),
                })

                const data = await res.json();

                const userDetailsRes = await fetch('/api/user_details', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': data.response.user.authentication_token
                    },
                });

                if (res.ok) {
                    localStorage.setItem( // This is a cruical step as it allows easy access of this resource to authenticate and give access to the respective user BASED ON THEIR ROLE.
                        'auth-token',
                        data.response.user.authentication_token
                    )

                    if (!userDetailsRes.ok) {
                        throw new Error("Failed to fetch user details.");
                    }

                    const userDetails = await userDetailsRes.json();
                    localStorage.setItem('userId', userDetails.id);
                    const userId = localStorage.getItem('userId');
                    this.$router.push(`/profile/${userId}`);
                }

            } catch {
                const res = await fetch('/login?include_auth_token', {
                    method: 'post',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.formData),
                })
                const data = await res.json();
                this.error = data.response.errors[0];
            }
        },
    },
}


export default login;