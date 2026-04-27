// API Configuration
const API_BASE_URL = 'http://localhost:3000/api';

// DOM Elements
const emailSection = document.getElementById('emailSection');
const otpSection = document.getElementById('otpSection');
const passwordSection = document.getElementById('passwordSection');
const loginSection = document.getElementById('loginSection');
const successSection = document.getElementById('successSection');

const emailInput = document.getElementById('email');
const regPasswordInput = document.getElementById('regPassword');
const otpInput = document.getElementById('otp');
const loginEmailInput = document.getElementById('loginEmail');
const loginPasswordInput = document.getElementById('loginPassword');

const emailDisplay = document.getElementById('emailDisplay');
const errorMessage = document.getElementById('errorMessage');
const successTitle = document.getElementById('successTitle');
const successMessage = document.getElementById('successMessage');

const sendOtpBtn = document.getElementById('sendOtpBtn');
const verifyOtpBtn = document.getElementById('verifyOtpBtn');
const loginBtn = document.getElementById('loginBtn');
const resendBtn = document.getElementById('resendBtn');
const backBtn = document.getElementById('backBtn');
const doneBtn = document.getElementById('doneBtn');

const registerModeBtn = document.getElementById('registerModeBtn');
const loginModeBtn = document.getElementById('loginModeBtn');

// State
let currentEmail = '';
let currentPassword = '';
let currentMode = 'register'; // 'register' or 'login'

// Utility Functions
function showSection(section) {
    [emailSection, otpSection, passwordSection, loginSection, successSection].forEach(s => s.classList.remove('active'));
    section.classList.add('active');
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => errorMessage.classList.remove('show'), 5000);
}

function setLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// API Functions
async function sendOTP(email) {
    const response = await fetch(`${API_BASE_URL}/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Failed to send OTP');
    return data;
}

async function verifyOTP(email, otp) {
    const response = await fetch(`${API_BASE_URL}/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Failed to verify OTP');
    return data;
}

async function registerUser(email, password) {
    const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Registration failed');
    return data;
}

async function loginUser(email, password) {
    const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Login failed');
    return data;
}

// Mode Toggle
registerModeBtn.addEventListener('click', () => {
    currentMode = 'register';
    registerModeBtn.classList.add('active');
    loginModeBtn.classList.remove('active');
    showSection(emailSection);
    clearForms();
});

loginModeBtn.addEventListener('click', () => {
    currentMode = 'login';
    loginModeBtn.classList.add('active');
    registerModeBtn.classList.remove('active');
    showSection(loginSection);
    clearForms();
});

function clearForms() {
    emailInput.value = '';
    regPasswordInput.value = '';
    otpInput.value = '';
    loginEmailInput.value = '';
    loginPasswordInput.value = '';
    errorMessage.classList.remove('show');
}

// Registration Flow
sendOtpBtn.addEventListener('click', async () => {
    const email = emailInput.value.trim();
    const password = regPasswordInput.value.trim();

    if (!email) {
        showError('Please enter your email address');
        emailInput.focus();
        return;
    }

    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        emailInput.focus();
        return;
    }

    if (!password) {
        showError('Please enter a password');
        regPasswordInput.focus();
        return;
    }

    if (password.length < 8) {
        showError('Password must be at least 8 characters long');
        regPasswordInput.focus();
        return;
    }

    setLoading(sendOtpBtn, true);

    try {
        await sendOTP(email);
        currentEmail = email;
        currentPassword = password;
        emailDisplay.textContent = email;
        showSection(otpSection);
        otpInput.focus();
        errorMessage.classList.remove('show');
    } catch (error) {
        showError(error.message || 'Failed to send OTP. Please try again.');
    } finally {
        setLoading(sendOtpBtn, false);
    }
});

verifyOtpBtn.addEventListener('click', async () => {
    const otp = otpInput.value.trim();

    if (!otp) {
        showError('Please enter the OTP');
        otpInput.focus();
        return;
    }

    if (otp.length !== 6 || !/^\d+$/.test(otp)) {
        showError('Please enter a valid 6-digit OTP');
        otpInput.focus();
        return;
    }

    setLoading(verifyOtpBtn, true);

    try {
        // Verify OTP
        await verifyOTP(currentEmail, otp);

        // Register user after OTP verification
        await registerUser(currentEmail, currentPassword);

        successTitle.textContent = 'Registration Successful!';
        successMessage.textContent = `Welcome! Your account has been created for ${currentEmail}`;
        showSection(successSection);

        // Clear sensitive data
        currentPassword = '';
        emailInput.value = '';
        regPasswordInput.value = '';
        otpInput.value = '';
        errorMessage.classList.remove('show');
    } catch (error) {
        showError(error.message || 'Failed to complete registration. Please try again.');
        otpInput.value = '';
        otpInput.focus();
    } finally {
        setLoading(verifyOtpBtn, false);
    }
});

// Login Flow
loginBtn.addEventListener('click', async () => {
    const email = loginEmailInput.value.trim();
    const password = loginPasswordInput.value.trim();

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    setLoading(loginBtn, true);

    try {
        const result = await loginUser(email, password);

        successTitle.textContent = 'Login Successful!';
        successMessage.textContent = `Welcome back, ${result.user.email}!`;
        showSection(successSection);

        loginEmailInput.value = '';
        loginPasswordInput.value = '';
        errorMessage.classList.remove('show');
    } catch (error) {
        showError(error.message || 'Login failed. Please check your credentials.');
        loginPasswordInput.value = '';
        loginPasswordInput.focus();
    } finally {
        setLoading(loginBtn, false);
    }
});

// Resend OTP
resendBtn.addEventListener('click', async () => {
    setLoading(resendBtn, true);
    try {
        await sendOTP(currentEmail);
        showError('OTP sent successfully! Check your email.');
        otpInput.value = '';
        otpInput.focus();
    } catch (error) {
        showError(error.message || 'Failed to resend OTP. Please try again.');
    } finally {
        setLoading(resendBtn, false);
    }
});

// Navigation
backBtn.addEventListener('click', () => {
    showSection(emailSection);
    otpInput.value = '';
    errorMessage.classList.remove('show');
});

doneBtn.addEventListener('click', () => {
    currentEmail = '';
    currentPassword = '';
    clearForms();
    showSection(currentMode === 'register' ? emailSection : loginSection);
});

// Password Toggle
document.getElementById('regPasswordToggle')?.addEventListener('click', function () {
    const input = regPasswordInput;
    input.type = input.type === 'password' ? 'text' : 'password';
});

document.getElementById('passwordToggle3')?.addEventListener('click', function () {
    const input = loginPasswordInput;
    input.type = input.type === 'password' ? 'text' : 'password';
});

// Enter key handlers
emailInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') regPasswordInput.focus();
});

regPasswordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendOtpBtn.click();
});

otpInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') verifyOtpBtn.click();
});

loginEmailInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') loginPasswordInput.focus();
});

loginPasswordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') loginBtn.click();
});

// Only allow numbers in OTP input
otpInput.addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/[^0-9]/g, '');
});

// Auto-focus
window.addEventListener('load', () => {
    emailInput.focus();
});
