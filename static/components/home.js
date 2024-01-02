// Here, the home.js component provides the interface for the landing page of our application
const home = {
    template: `<div>
    <div class="welcome-section">
        <div class="welcome-text">
            <h1>Welcome to E-Bazaar</h1>
            <br>
            <p>Discover a world of fresh and quality groceries at your fingertips. Explore our wide range of products
                and enjoy a seamless shopping experience.</p>
        </div>
    </div>
    <div class="small-text-section">
        <h2>About Us</h2>
        <p>This is a project developed as a part of the IIT Madras BS Data Science and Applications program, under the Modern Application
        Development II Project.</p>
    </div>
    </div>`,

    data() {
        return {
            userId: 0,
        }
    }
}



export default home