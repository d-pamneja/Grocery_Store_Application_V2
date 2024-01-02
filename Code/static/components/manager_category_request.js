// Here, the manager_category_request.js component provides the interface for the manager to make requests to admin for categories.
const StoreManagerRequest = {
    template: `
    <div class="center-box bg-white rounded">
        <h2>Category Request</h2>
        
        <div class="input-container">
            <label for="selectedAction">Select Action:</label>
            <select v-model="selectedAction" @change="resetForm">
                <option value="add">Add</option>
                <option value="edit">Edit</option>
                <option value="remove">Remove</option>
            </select>
        </div>

        <br>
  
        <div v-if="selectedAction === 'add'" >
            <div class="input-container">
                <label for="categoryName">Enter Category Name :</label>
                <input v-model="categoryName" placeholder="Category Name" />
            </div>
            <br>
            <div class="input-container">
                <label for="description">Enter Description :</label>
                <input v-model="description" placeholder="Description"></input>
            </div>
        </div>
  
        <div v-if="selectedAction === 'edit'">
            <div class="input-container">
                <label for="selectedCategory">Select a category:</label>
                <select v-model="selectedCategory">
                    <option v-for="category in categories" :value="category.id" >{{ category.name }}</option>
                </select>
            </div>
            <br>
            <div class="input-container">
                <label for="categoryName">Enter Category Name :</label>
                <input v-model="categoryName" placeholder="Category Name" />
            </div>
            <br>
            <div class="input-container">
                <label for="description">Enter Description :</label>
                <input v-model="description" placeholder="Description..."></input>
            </div>
            <br>
            <div class="input-container">
                <label for="reason">Enter Reason :</label>
                <input v-model="reason" placeholder="Reason..."></input>
            </div>
        </div>

        <div v-if="selectedAction === 'remove'">
            <div class="input-container">
                <label for="selectedCategory">Select a category:</label>
                <select v-model="selectedCategory">
                    <option v-for="category in categories" :value="category.id">{{ category.name }}</option>
                </select>
            </div>
            <br>
            <div class="input-container">
                <label for="reason">Enter Reason :</label>
                <input v-model="reason" placeholder="Reason.."></input>
            </div>
        </div>
  
        <br>
        <button @click="submitRequest" class="btn btn-outline-primary-2">Submit Request</button>
        <br><br>
        <p v-if="errorform" style="color: red">{{ errorform }}</p>
        <br>
        <button @click="goToStoreManagerDashboard" class="btn btn-outline-primary">Go back to Store Manager Dashboard</button>
    </div>
    `,
    data() {
        return {
            selectedAction: 'add',
            categoryName: '',
            description: '',
            selectedCategory: null,
            reason: '',
            categories: [],
            errorform: null
        }
    },
    async mounted() {
        const response = await fetch('/api/view_categories', {
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (response.ok) {
            this.categories = await response.json();
        } else {
            this.success = false
            this.error = 'Failed to fetch categories.';
        }
    },

    methods: {
        resetForm() {
            this.categoryName = '';
            this.description = '';
            this.reason = '';
            this.selectedCategory = null;
            this.errorform = null;
        },
        async submitRequest() {
            let delCategoryName = this.categoryName
            let delCategoryDescription = this.description

            if (this.selectedAction == 'remove') {
                delCategoryName = "NA";
                delCategoryDescription = "NA";
            }


            const requestData = {
                action: this.selectedAction,
                name: delCategoryName,
                description: delCategoryDescription,
                selectedCategory: this.selectedCategory,
                reason: this.reason
            };

            if (this.selectedAction === 'add' && !this.categoryName.trim()) {
                this.errorform = 'Category Name is required.';
                return;
            } else if (this.selectedAction === 'edit' && !this.categoryName.trim()) {
                this.errorform = 'Category Name is required.';
                return;
            } else if (this.selectedAction === 'edit' && !this.reason.trim()) {
                this.errorform = 'Reason to edit category is required.';
                return;
            } else if (this.selectedAction === 'remove' && !this.reason.trim()) {
                this.errorform = 'Reason to delete category is required.';
                return;
            } else if (this.selectedAction != 'add' && !this.selectedCategory) {
                this.errorform = 'Category is required to modify it.';
                return;
            }



            const response = await fetch('/api/category_requests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': localStorage.getItem('auth-token'),
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                alert('Request submitted successfully!');
                this.resetForm();
                this.errorform = null;
                this.$router.push('/store_manager_dashboard');
            } else {
                const errorMessage = await response.text();
                this.errorform = errorMessage.message;
            }
        },
        goToStoreManagerDashboard() {
            this.$router.push('/store_manager_dashboard')
        }
    }
};

export default StoreManagerRequest;