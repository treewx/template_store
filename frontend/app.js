const API_BASE_URL = 'http://localhost:5000';

function showLogin() {
    document.querySelector('.welcome-card').classList.add('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
}

function showSignup() {
    document.querySelector('.welcome-card').classList.add('hidden');
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
}

function showWelcome() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.querySelector('.welcome-card').classList.remove('hidden');
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

document.addEventListener('DOMContentLoaded', function() {
    testAPIConnection();
    
    const loginForm = document.querySelector('#loginForm form');
    const signupForm = document.querySelector('#signupForm form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Login form submitted');
        });
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Signup form submitted');
        });
    }
});