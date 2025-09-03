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
        const response = await fetch(`${API_BASE_URL}/api/health`);
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
                <button onclick="showBankConnection()" class="btn btn-primary">Bank Connection</button>
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
                <h4>${property.address || 'Property #' + property.id}</h4>
                <div class="property-actions">
                    <button onclick="editProperty(${property.id})" class="btn btn-small">Edit</button>
                    <button onclick="removeProperty(${property.id})" class="btn btn-small btn-danger">Delete</button>
                </div>
            </div>
            <div class="property-details">
                <p><strong>Payment Keyword:</strong> ${property.keyword || 'Not set'}</p>
                <p><strong>Rent:</strong> $${property.rent_amount} ${property.frequency}</p>
                <p><strong>Due Day:</strong> ${property.due_day.charAt(0).toUpperCase() + property.due_day.slice(1)}s</p>
                <p><strong>Balance:</strong> <span class="balance ${property.balance >= 0 ? 'positive' : 'negative'}">${property.balance >= 0 ? '+' : ''}$${property.balance}</span></p>
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
            
            <input type="text" name="address" placeholder="Property Address *" required 
                   value="${isEdit ? (property.address || '') : ''}" />
            
            <input type="text" name="keyword" placeholder="Payment Keyword *" required 
                   value="${isEdit ? (property.keyword || '') : ''}" />
                   
            <input type="number" name="rent_amount" placeholder="Rent Amount *" required 
                   step="0.01" min="0" value="${isEdit ? property.rent_amount : ''}" />
            
            <select name="frequency" required>
                <option value="">Select Frequency *</option>
                <option value="weekly" ${isEdit && property.frequency === 'weekly' ? 'selected' : ''}>Weekly</option>
                <option value="fortnightly" ${isEdit && property.frequency === 'fortnightly' ? 'selected' : ''}>Fortnightly</option>
                <option value="monthly" ${isEdit && property.frequency === 'monthly' ? 'selected' : ''}>Monthly</option>
            </select>
            
            <select name="due_day" required>
                <option value="">Select Due Day *</option>
                <option value="monday" ${isEdit && property.due_day === 'monday' ? 'selected' : ''}>Monday</option>
                <option value="tuesday" ${isEdit && property.due_day === 'tuesday' ? 'selected' : ''}>Tuesday</option>
                <option value="wednesday" ${isEdit && property.due_day === 'wednesday' ? 'selected' : ''}>Wednesday</option>
                <option value="thursday" ${isEdit && property.due_day === 'thursday' ? 'selected' : ''}>Thursday</option>
                <option value="friday" ${isEdit && property.due_day === 'friday' ? 'selected' : ''}>Friday</option>
                <option value="saturday" ${isEdit && property.due_day === 'saturday' ? 'selected' : ''}>Saturday</option>
                <option value="sunday" ${isEdit && property.due_day === 'sunday' ? 'selected' : ''}>Sunday</option>
            </select>
            
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
        address: formData.get('address'),
        keyword: formData.get('keyword'),
        rent_amount: parseFloat(formData.get('rent_amount')),
        frequency: formData.get('frequency'),
        due_day: formData.get('due_day'),
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

// Bank Connection Functions
async function showBankConnection() {
    clearDashboardSelection();
    document.querySelector('#dashboardContent').innerHTML = `
        <div class="bank-connection">
            <h3>Bank Connection</h3>
            <div class="bank-status">
                <h4>Connection Status</h4>
                <div id="bankStatusContainer">
                    <p>Loading bank status...</p>
                </div>
            </div>
            
            <div class="demo-connection">
                <h4>Demo Mode - Test Connection</h4>
                <p>In demo mode, you can test the bank connection functionality with mock data.</p>
                <div class="form-group">
                    <label for="testToken">Test Token (optional):</label>
                    <input type="text" id="testToken" placeholder="Leave blank to use demo token" />
                    <small>In production, you would enter your actual Akahu access token here.</small>
                </div>
                <div class="form-actions">
                    <button onclick="testBankConnection()" class="btn btn-primary">Test Connection</button>
                    <button onclick="connectBankOAuth()" class="btn btn-success">🏦 Connect Real Bank Account</button>
                    <button onclick="connectBank()" class="btn btn-secondary">Connect Demo Bank (Testing)</button>
                </div>
                <div class="help-text" style="margin-top: 1rem; padding: 1rem; background: #f8f9fa; border-radius: 8px; font-size: 0.9rem;">
                    <p style="margin: 0.5rem 0;"><strong>🔐 Real Bank Connection:</strong> Secure OAuth flow through Akahu's official wizard</p>
                    <p style="margin: 0.5rem 0;"><strong>🧪 Demo Connection:</strong> For testing with mock transaction data</p>
                </div>
            </div>
            
            <div id="bankTestResults" class="hidden">
                <h4>Connection Test Results</h4>
                <div id="testResultsContent"></div>
            </div>
            
            <div id="connectedAccounts" class="hidden">
                <h4>Connected Accounts</h4>
                <div id="accountsList"></div>
                <div class="sync-section">
                    <h5>Sync Transactions</h5>
                    <p>Select a property and account to sync recent transactions:</p>
                    <div class="sync-form">
                        <select id="propertySelect">
                            <option value="">Select Property...</option>
                        </select>
                        <select id="accountSelect">
                            <option value="">Select Account...</option>
                        </select>
                        <button onclick="syncTransactions()" class="btn btn-primary" disabled>Sync Transactions</button>
                    </div>
                    <div id="syncResults"></div>
                </div>
            </div>
        </div>
    `;
    
    // Clear active states
    document.querySelectorAll('.dashboard-nav button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('button[onclick="showBankConnection()"]').classList.add('active');
    
    // Load initial status
    await loadBankStatus();
    await loadPropertiesForSync();
}

async function loadBankStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/bank/status`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const status = await response.json();
            const container = document.getElementById('bankStatusContainer');
            
            container.innerHTML = `
                <div class="status-card ${status.connected ? 'connected' : 'disconnected'}">
                    <p><strong>Status:</strong> ${status.connected ? '✅ Connected' : '❌ Not Connected'}</p>
                    <p><strong>Accounts:</strong> ${status.accounts_count || 0}</p>
                    <p><strong>Last Sync:</strong> ${status.last_sync || 'Never'}</p>
                    ${status.demo_mode ? '<p><strong>Mode:</strong> 🧪 Demo Mode</p>' : ''}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading bank status:', error);
    }
}

async function testBankConnection() {
    const testToken = document.getElementById('testToken').value || 'mock_token';
    const resultsContainer = document.getElementById('bankTestResults');
    const contentContainer = document.getElementById('testResultsContent');
    
    try {
        contentContainer.innerHTML = '<p>Testing connection...</p>';
        resultsContainer.classList.remove('hidden');
        
        const response = await fetch(`${API_BASE_URL}/api/bank/test-connection`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ test_token: testToken })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            contentContainer.innerHTML = `
                <div class="test-success">
                    <p>✅ <strong>Connection successful!</strong></p>
                    <p><strong>Accounts found:</strong> ${result.accounts_found}</p>
                    <p><strong>Sample transactions:</strong> ${result.sample_transactions}</p>
                    
                    <h5>Sample Accounts:</h5>
                    <ul>
                        ${result.test_data.accounts.map(acc => 
                            `<li><strong>${acc.name}</strong> (${acc.bank}) - ${acc.type}</li>`
                        ).join('')}
                    </ul>
                    
                    <h5>Recent Transactions (sample):</h5>
                    <ul>
                        ${result.test_data.recent_transactions.map(txn => 
                            `<li>$${txn.amount} - ${txn.description} (${txn.date.split('T')[0]})</li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        } else {
            contentContainer.innerHTML = `
                <div class="test-error">
                    <p>❌ <strong>Connection failed</strong></p>
                    <p>${result.error || 'Unknown error occurred'}</p>
                </div>
            `;
        }
    } catch (error) {
        contentContainer.innerHTML = `
            <div class="test-error">
                <p>❌ <strong>Connection failed</strong></p>
                <p>Network error: ${error.message}</p>
            </div>
        `;
    }
}

async function connectBankOAuth() {
    /**
     * Start Akahu OAuth connection flow
     * This opens Akahu's secure connection wizard
     */
    try {
        // Step 1: Get OAuth authorization URL from backend
        const response = await fetch(`${API_BASE_URL}/api/bank/connect/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Step 2: Open Akahu's OAuth page in popup
            const popup = window.open(
                result.auth_url,
                'akahu_connect',
                'width=600,height=700,scrollbars=yes,resizable=yes'
            );
            
            // Step 3: Listen for completion
            const messageListener = (event) => {
                if (event.data.type === 'AKAHU_CONNECTION_SUCCESS') {
                    window.removeEventListener('message', messageListener);
                    
                    // Show success message
                    alert(`✅ Bank connected successfully! Found ${event.data.accounts} account(s).`);
                    
                    // Refresh the page to show updated bank status
                    location.reload();
                }
            };
            
            window.addEventListener('message', messageListener);
            
            // Monitor if popup was closed without completing
            const popupChecker = setInterval(() => {
                if (popup.closed) {
                    clearInterval(popupChecker);
                    window.removeEventListener('message', messageListener);
                }
            }, 1000);
            
        } else {
            const error = await response.json();
            alert(`Failed to start bank connection: ${error.error}`);
        }
    } catch (error) {
        console.error('Error starting bank connection:', error);
        alert('Failed to start bank connection');
    }
}

async function connectBank() {
    const testToken = document.getElementById('testToken').value || 'mock_demo_token';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/bank/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ access_token: testToken })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Show connected accounts
            const accountsContainer = document.getElementById('connectedAccounts');
            const accountsList = document.getElementById('accountsList');
            const accountSelect = document.getElementById('accountSelect');
            
            accountsList.innerHTML = `
                <div class="accounts-grid">
                    ${result.accounts.map(acc => `
                        <div class="account-card">
                            <h5>${acc.name}</h5>
                            <p><strong>Bank:</strong> ${acc.bank}</p>
                            <p><strong>Type:</strong> ${acc.type}</p>
                            <p><strong>ID:</strong> ${acc.id}</p>
                        </div>
                    `).join('')}
                </div>
            `;
            
            // Populate account select
            accountSelect.innerHTML = '<option value="">Select Account...</option>' +
                result.accounts.map(acc => 
                    `<option value="${acc.id}">${acc.name} (${acc.bank})</option>`
                ).join('');
            
            accountsContainer.classList.remove('hidden');
            
            // Update status
            await loadBankStatus();
            
            alert('Demo bank connected successfully! You can now sync transactions.');
        } else {
            alert(`Failed to connect bank: ${result.error}`);
        }
    } catch (error) {
        console.error('Error connecting bank:', error);
        alert('Failed to connect bank account');
    }
}

async function loadPropertiesForSync() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/properties`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            const propertySelect = document.getElementById('propertySelect');
            
            propertySelect.innerHTML = '<option value="">Select Property...</option>' +
                data.properties.map(prop => 
                    `<option value="${prop.id}">${prop.name} - $${prop.rent_amount} ${prop.frequency}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('Error loading properties for sync:', error);
    }
}

async function syncTransactions() {
    const propertyId = document.getElementById('propertySelect').value;
    const accountId = document.getElementById('accountSelect').value;
    const resultsContainer = document.getElementById('syncResults');
    
    if (!propertyId || !accountId) {
        alert('Please select both a property and an account');
        return;
    }
    
    try {
        resultsContainer.innerHTML = '<p>Syncing transactions...</p>';
        
        const response = await fetch(`${API_BASE_URL}/api/bank/sync/${propertyId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ account_id: accountId })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            resultsContainer.innerHTML = `
                <div class="sync-success">
                    <p>✅ <strong>Sync completed!</strong></p>
                    <p><strong>Transactions found:</strong> ${result.transactions_found}</p>
                    <p><strong>Transactions stored:</strong> ${result.transactions_stored}</p>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `
                <div class="sync-error">
                    <p>❌ <strong>Sync failed</strong></p>
                    <p>${result.error}</p>
                </div>
            `;
        }
    } catch (error) {
        resultsContainer.innerHTML = `
            <div class="sync-error">
                <p>❌ <strong>Sync failed</strong></p>
                <p>Network error: ${error.message}</p>
            </div>
        `;
    }
}

// Enable sync button when both selects have values
document.addEventListener('change', function(e) {
    if (e.target.id === 'propertySelect' || e.target.id === 'accountSelect') {
        const propertySelect = document.getElementById('propertySelect');
        const accountSelect = document.getElementById('accountSelect');
        const syncButton = document.querySelector('button[onclick="syncTransactions()"]');
        
        if (propertySelect && accountSelect && syncButton) {
            syncButton.disabled = !(propertySelect.value && accountSelect.value);
        }
    }
});

function clearDashboardSelection() {
    document.querySelectorAll('.dashboard-nav button').forEach(btn => {
        btn.classList.remove('active');
    });
}