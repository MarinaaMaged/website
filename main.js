import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBKV7uRb5YUUdkulVgqcFQsw9g1ffrOLs0",
  authDomain: "flutter-844ee.firebaseapp.com",
  databaseURL: "https://flutter-844ee-default-rtdb.firebaseio.com",
  projectId: "flutter-844ee",
  storageBucket: "flutter-844ee.appspot.com",
  messagingSenderId: "344608236578",
  appId: "1:344608236578:web:04be4a87ae2847aff8167b",
  measurementId: "G-0H0Y629943"

};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

document.addEventListener("DOMContentLoaded", () => {
    // DOM elements for sign-in and sign-up modes
    const signinBtn = document.querySelector("#sign-in-btn");
    const signupBtn = document.querySelector("#sign-up-btn");
    const container = document.querySelector(".container");

    signupBtn.addEventListener('click', () => {
        container.classList.add("sign-up-mode");
    });

    signinBtn.addEventListener('click', () => {
        container.classList.remove("sign-up-mode");
    });

    // Handle form submission for login
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            console.log('Logged in successfully:', userCredential);
            window.location.href = 'home.html'; // Redirect to home.html
        } catch (error) {
            console.error('Error logging in:', error.message);
            alert('Login failed: ' + error.message);
        }
    });

    // Handle form submission for signup
    const signupForm = document.querySelector('.sign-up-form');
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = signupForm.querySelector('input[type="email"]').value;
        const password = signupForm.querySelector('input[type="password"]').value;

        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            console.log('User registered successfully:', userCredential);
            alert('Signup successful! Please log in.');
            container.classList.remove("sign-up-mode"); // Switch to login mode
        } catch (error) {
            console.error('Error signing up:', error.message);
            alert('Signup failed: ' + error.message);
        }
    });
});
