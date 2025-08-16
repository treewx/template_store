const API_BASE_URL = 'http://localhost:5000';

function showLogin() {
    document.querySelector('.welcome-card').classList.add('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
    clearMessages();
}

function showSignup() {
    document.querySelector('.welcome-card').classList.add('hidden');
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
    clearMessages();
}

function showWelcome() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.querySelector('.welcome-card').classList.remove('hidden');
    clearMessages();
}

function showMessage(element, message, type = 'error') {
    const messageDiv = element.querySelector('.message') || document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    if (!element.querySelector('.message')) {
        element.insertBefore(messageDiv, element.querySelector('form'));
    }
}

function clearMessages() {
    document.querySelectorAll('.message').forEach(msg => msg.remove());
}

function showLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = 'Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.dataset.originalText || button.textContent;
    }
}

async function testAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('API Health Check:', data);
        return true;
    } catch (error) {
        console.error('API connection failed:', error);
        return false;
    }
}

async function register(email, password, confirmPassword) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                email: email,
                password: password,
                confirm_password: confirmPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data: data };
        } else {
            return { success: false, error: data.error || 'Registration failed' };
        }
    } catch (error) {
        console.error('Registration error:', error);
        return { success: false, error: 'Network error. Please try again.' };
    }
}

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data: data };
        } else {
            return { success: false, error: data.error || 'Login failed' };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error. Please try again.' };
    }
}

async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            return { success: true, user: data.user };
        } else {
            return { success: false };
        }
    } catch (error) {
        console.error('Get current user error:', error);
        return { success: false };
    }
}

function handleUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (window.location.pathname === '/verify-email' && token) {
        verifyEmail(token);
    } else if (window.location.pathname === '/reset-password' && token) {
        showPasswordReset(token);
    }
}

async function verifyEmail(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/verify-email/${token}`);
        const data = await response.json();
        
        if (response.ok) {
            alert('Email verified successfully! You can now log in.');
            window.location.href = '/';
        } else {
            alert('Verification failed: ' + data.error);
        }
    } catch (error) {
        alert('Verification failed. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    testAPIConnection();
    handleUrlParams();
    
    // Check if user is already logged in
    getCurrentUser().then(result => {
        if (result.success) {
            showDashboard(result.user);
        }
    });
    
    const loginForm = document.querySelector('#loginForm form');
    const signupForm = document.querySelector('#signupForm form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitButton = this.querySelector('button[type="submit"]');
            const email = this.querySelector('input[type="email"]').value;
            const password = this.querySelector('input[type="password"]').value;
            
            showLoading(submitButton, true);
            clearMessages();
            
            const result = await login(email, password);
            
            showLoading(submitButton, false);
            
            if (result.success) {
                showMessage(document.getElementById('loginForm'), 'Login successful!', 'success');
                setTimeout(() => {
                    showDashboard(result.data.user);
                }, 1000);
            } else {
                showMessage(document.getElementById('loginForm'), result.error);
            }
        });
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitButton = this.querySelector('button[type="submit"]');
            const email = this.querySelector('input[type="email"]').value;
            const password = this.querySelector('input[type="password"]').value;
            const confirmPassword = this.querySelectorAll('input[type="password"]')[1].value;
            
            showLoading(submitButton, true);
            clearMessages();
            
            const result = await register(email, password, confirmPassword);
            
            showLoading(submitButton, false);
            
            if (result.success) {
                showMessage(document.getElementById('signupForm'), 
                    'Registration successful! Please check your email for verification.', 'success');
                this.reset();
            } else {
                showMessage(document.getElementById('signupForm'), result.error);
            }
        });
    }
});

function showDashboard(user) {
    document.querySelector('main').innerHTML = `
        <div class="dashboard">
            <h2>Welcome, ${user.email}!</h2>
            <div class="dashboard-nav">
                <button onclick="showProperties()" class="btn btn-primary">Manage Properties</button>
                <button onclick="logout()" class="btn btn-secondary">Logout</button>
            </div>
            <div id="dashboardContent">
                <p>Select an option above to get started.</p>
            </div>
        </div>
    `;
}

async function loadProperties() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/properties`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            return { success: true, properties: data.properties };
        } else {
            return { success: false, error: 'Failed to load properties' };
        }
    } catch (error) {
        console.error('Load properties error:', error);
        return { success: false, error: 'Network error' };
    }
}

async function createProperty(propertyData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/properties`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(propertyData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, property: data.property };
        } else {
            return { success: false, error: data.error || 'Failed to create property' };
        }
    } catch (error) {
        console.error('Create property error:', error);
        return { success: false, error: 'Network error' };
    }
}

async function updateProperty(propertyId, propertyData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/properties/${propertyId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(propertyData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, property: data.property };
        } else {
            return { success: false, error: data.error || 'Failed to update property' };
        }
    } catch (error) {
        console.error('Update property error:', error);
        return { success: false, error: 'Network error' };
    }
}

async function deleteProperty(propertyId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/properties/${propertyId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            return { success: true };
        } else {
            const data = await response.json();
            return { success: false, error: data.error || 'Failed to delete property' };
        }
    } catch (error) {
        console.error('Delete property error:', error);
        return { success: false, error: 'Network error' };
    }
}

async function showProperties() {
    const content = document.getElementById('dashboardContent');
    content.innerHTML = '<p>Loading properties...</p>';
    
    const result = await loadProperties();
    
    if (result.success) {
        const properties = result.properties;
        
        content.innerHTML = `
            <div class="properties-section">
                <div class="section-header">
                    <h3>Your Properties</h3>
                    <button onclick="showAddPropertyForm()" class="btn btn-primary">Add Property</button>
                </div>
                
                <div id="propertiesList">
                    ${properties.length === 0 ? 
                        '<p class="no-data">No properties yet. Add your first property to get started!</p>' :
                        properties.map(prop => createPropertyCard(prop)).join('')
                    }
                </div>
                
                <div id="propertyFormContainer" class="hidden">
                    ${createPropertyForm()}
                </div>
            </div>
        `;
    } else {
        content.innerHTML = `<p class="error">Failed to load properties: ${result.error}</p>`;
    }
}

function createPropertyCard(property) {
    return `
        <div class="property-card" data-id="${property.id}">
            <div class="property-header">
                <h4>${property.name}</h4>
                <div class="property-actions">
                    <button onclick="editProperty(${property.id})" class="btn btn-small">Edit</button>
                    <button onclick="removeProperty(${property.id})" class="btn btn-small btn-danger">Delete</button>
                </div>
            </div>
            <div class="property-details">
                ${property.address ? `<p><strong>Address:</strong> ${property.address}</p>` : ''}
                <p><strong>Rent:</strong> $${property.rent_amount} ${property.frequency}</p>
                <p><strong>Due Day:</strong> ${property.due_day}${property.frequency === 'monthly' ? ' of each month' : ''}</p>
                ${property.tenant_nickname ? `<p><strong>Tenant:</strong> ${property.tenant_nickname}</p>` : ''}
            </div>
        </div>
    `;
}

function createPropertyForm(property = null) {
    const isEdit = property !== null;
    return `
        <form class="property-form" onsubmit="handlePropertySubmit(event, ${isEdit ? property.id : 'null'})">
            <h4>${isEdit ? 'Edit' : 'Add'} Property</h4>
            
            <input type="text" name="name" placeholder="Property Name *" required 
                   value="${isEdit ? property.name : ''}" />
            
            <input type="text" name="address" placeholder="Address (optional)" 
                   value="${isEdit ? (property.address || '') : ''}" />
            
            <input type="number" name="rent_amount" placeholder="Rent Amount *" required 
                   step="0.01" min="0" value="${isEdit ? property.rent_amount : ''}" />
            
            <select name="frequency" required>
                <option value="">Select Frequency *</option>
                <option value="weekly" ${isEdit && property.frequency === 'weekly' ? 'selected' : ''}>Weekly</option>
                <option value="fortnightly" ${isEdit && property.frequency === 'fortnightly' ? 'selected' : ''}>Fortnightly</option>
                <option value="monthly" ${isEdit && property.frequency === 'monthly' ? 'selected' : ''}>Monthly</option>
            </select>
            
            <input type="number" name="due_day" placeholder="Due Day (1-31) *" required 
                   min="1" max="31" value="${isEdit ? property.due_day : ''}" />
            
            <input type="text" name="tenant_nickname" placeholder="Tenant Nickname (optional)" 
                   value="${isEdit ? (property.tenant_nickname || '') : ''}" />
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">${isEdit ? 'Update' : 'Add'} Property</button>
                <button type="button" onclick="hidePropertyForm()" class="btn btn-secondary">Cancel</button>
            </div>
        </form>
    `;
}

function showAddPropertyForm() {
    const container = document.getElementById('propertyFormContainer');
    container.innerHTML = createPropertyForm();
    container.classList.remove('hidden');
    document.querySelector('.section-header button').style.display = 'none';
}

function hidePropertyForm() {
    const container = document.getElementById('propertyFormContainer');
    container.classList.add('hidden');
    document.querySelector('.section-header button').style.display = 'inline-block';
}

async function handlePropertySubmit(event, propertyId) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);
    
    const propertyData = {
        name: formData.get('name'),
        address: formData.get('address'),
        rent_amount: parseFloat(formData.get('rent_amount')),
        frequency: formData.get('frequency'),
        due_day: parseInt(formData.get('due_day')),
        tenant_nickname: formData.get('tenant_nickname')
    };
    
    showLoading(submitButton, true);
    clearMessages();
    
    let result;
    if (propertyId) {
        result = await updateProperty(propertyId, propertyData);
    } else {
        result = await createProperty(propertyData);
    }
    
    showLoading(submitButton, false);
    
    if (result.success) {
        hidePropertyForm();
        showProperties(); // Refresh the list
    } else {
        showMessage(form.parentElement, result.error);
    }
}

async function editProperty(propertyId) {
    // Get property details
    try {
        const response = await fetch(`${API_BASE_URL}/api/properties/${propertyId}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const container = document.getElementById('propertyFormContainer');
            container.innerHTML = createPropertyForm(data.property);
            container.classList.remove('hidden');
            document.querySelector('.section-header button').style.display = 'none';
        }
    } catch (error) {
        alert('Failed to load property details');
    }
}

async function removeProperty(propertyId) {
    if (!confirm('Are you sure you want to delete this property?')) {
        return;
    }
    
    const result = await deleteProperty(propertyId);
    
    if (result.success) {
        showProperties(); // Refresh the list
    } else {
        alert('Failed to delete property: ' + result.error);
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        location.reload();
    } catch (error) {
        console.error('Logout error:', error);
        location.reload();
    }
}