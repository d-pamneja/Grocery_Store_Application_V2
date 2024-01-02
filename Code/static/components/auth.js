export async function fetchAndCheckUserRole(to, from, next) {
    try {
        const userId = localStorage.getItem('userId');
        const response = await fetch(`/api/user/${userId}/roles`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authentication-Token': localStorage.getItem('auth-token')
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user roles');
        }

        const data = await response.json();
        const userRoles = data.roles;

        const requiredRole = to.meta.requiresRole;
        if (requiredRole && !userRoles.includes(requiredRole)) {
            next('/invalid_auth_page');
        } else {
            next();
        }
    } catch (error) {
        console.error('Error fetching user roles:', error);
        next('/invalid_auth_page');
    }
}