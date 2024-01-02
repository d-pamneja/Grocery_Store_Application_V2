import home from "./components/home.js"
import profile from "./components/profile.js"
import login from "./components/login.js"
import register from "./components/register.js"
import invalid_auth_page from "./components/invalid_auth_page.js"
import { fetchAndCheckUserRole } from "./components/auth.js"

import admin_dashboard from "./components/admin_dashboard.js"
import create_category from "./components/create_category.js"
import view_categories from "./components/view_categories.js"
import edit_category from "./components/edit_category.js"
import delete_category from "./components/delete_category.js"
import AdminSettings from "./components/admin_settings.js"

import store_manager_dashboard from "./components/store_manager_dashboard.js"
import create_product from "./components/create_product.js"
import view_products from "./components/view_products.js"
import view_manager_categories from "./components/view_manager_categories.js"
import edit_product from "./components/edit_product.js"
import delete_product from "./components/delete_product.js"
import StoreManagerRequest from "./components/manager_category_request.js"
import AdminDisplayRequests from "./components/admin_category_requests.js"

import user_dashboard from "./components/user_dashboard.js"
import cartComponent from "./components/view_cart.js"
import orderSummaryComponent from "./components/order_summary.js"
import MyOrderHistoryComponent from "./components/my_orders.js"


const routes = [{
        path: '/',
        component: home,
    },
    {
        path: '/profile/:id',
        component: profile,
        beforeEnter: (to, from, next) => {
            const isAuthenticated = localStorage.getItem('auth-token');
            if (isAuthenticated) {
                next();
            } else {
                next('/login');
            }
        },
    },
    {
        path: '/invalid_auth_page',
        component: invalid_auth_page,
    },
    {
        path: '/login',
        component: login,
        beforeEnter: (to, from, next) => {
            const isAuthenticated = localStorage.getItem('auth-token');
            if (!isAuthenticated) {
                next();
            } else {
                next('/');
            }
        },
    },
    {
        path: '/register_app',
        component: register,
        beforeEnter: (to, from, next) => {
            const isAuthenticated = localStorage.getItem('auth-token');
            if (!isAuthenticated) {
                next();
            } else {
                next('/');
            }
        },
    },
    {
        path: '/admin_dashboard',
        component: admin_dashboard,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Admin' }
    },
    {
        path: '/create_category',
        component: create_category,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Admin' }
    },
    {
        path: '/view_categories',
        component: view_categories,
    },
    {
        path: '/edit_category/:id',
        component: edit_category,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Admin' }
    },
    {
        path: '/delete_category/:id',
        component: delete_category,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Admin' }
    },
    {
        path: '/admin_settings',
        component: AdminSettings,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Admin' }
    },
    {
        path: '/view_pending_requests',
        component: AdminDisplayRequests,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Admin' }
    },
    {
        path: '/store_manager_dashboard',
        component: store_manager_dashboard,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },
    {
        path: '/create_product',
        component: create_product,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },
    {
        path: '/view_products',
        component: view_products,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },
    {
        path: '/view_manager_categories',
        component: view_manager_categories,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },
    {
        path: '/edit_product/:id',
        component: edit_product,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },
    {
        path: '/delete_product/:id',
        component: delete_product,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },
    {
        path: '/category_requests',
        component: StoreManagerRequest,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'Store Manager' }
    },

    {
        path: '/user_dashboard',
        component: user_dashboard,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'User' }
    },
    {
        path: '/view_cart/:id',
        component: cartComponent,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'User' }
    },
    {
        path: '/get_latest_order/:id',
        component: orderSummaryComponent,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'User' }
    },
    {
        path: '/my_orders/:id',
        component: MyOrderHistoryComponent,
        beforeEnter: fetchAndCheckUserRole,
        meta: { requiresRole: 'User' }
    }

]

const router = new VueRouter({
    mode: 'history',
    routes,
    base: '/',
});

const app = new Vue({
    el: '#app',
    router,
    computed: {
        userId() {
            const storedUserId = localStorage.getItem('userId');
            return storedUserId ? storedUserId : 0;
        },
    },
    methods: {
        async logout() {
            const res = await fetch('/logout');
            if (res.ok) {
                localStorage.clear();
                this.$router.push('/');
            } else {
                console.log('Could not Log Out the User!');
            }
        },
    }
});