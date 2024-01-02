// Here, the invalid_auth_page.js component provides the interface for the case when encountered a page for which they do not have an access to
const invalid_auth_page = {
    template: `
    <div class="center-box bg-white rounded">
        <div class="invalid-auth-page">
            <h2>Unauthorized Access</h2>
            <p>
            We're sorry, but you do not have the authorization to access this page.
            Please contact the team for further assistance.
            </p>
            <div class="profile-buttons">
                <button @click="goToProfile">Return to Profile Page</button>
            </div>
        </div>
    </div>
  `,

    data() {
        return {
            userId: localStorage.getItem('userId'),
        }
    },

    methods: {
        goToProfile() {
            this.$router.push(`/profile/${this.userId}`);
        }
    }
}

export default invalid_auth_page;