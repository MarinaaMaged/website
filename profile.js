import { initializeApp } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-app.js";
import { getDatabase,  ref, set, get, child } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-database.js";

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


const socket = io('http://localhost:5001');
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);
async function startMqtt() {
    try {
        await fetch('http://localhost:5001/');
        console.log('MQTT client started');
    } catch (error) {
        console.error("Error starting MQTT:", error);
    }
}
function updateProfileData(data) {
    // Update text content
    document.getElementById('nameDisplay').textContent = data.Input.name;
    document.getElementById('weightDisplay').textContent = data.Input.weight + ' kg';
    document.getElementById('ageDisplay').textContent = data.Input.age+ ' years';
    document.getElementById('goalsDisplay').textContent = data.Input.goals;
}
async function fetchData() {
    try {
        const response = await fetch('http://localhost:5000/get_data');
        const data = await response.json();
        console.log("Fetched data:", data); // Log data for debugging
        if (response.ok) {
            updateProfileData(data); // Update dashboard with fetched data
        } else {
            console.error("Error fetching data:", data.error);
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

socket.on('connect', () => {
    console.log('Connected to the server');
});
// Listen for 'profile_data' event from the server
socket.on('profile_data',  (message) => {
    console.log("Received profile_data from server:", message);

    fetchData();
});

// Toggle profile form visibility
window.toggleProfileForm = function() {
    const formContainer = document.getElementById('profileFormContainer');
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
        formContainer.style.display = 'block';
    } else {
        formContainer.style.display = 'none';
    }
};

// Update Profile and send data to Firebase
window.updateProfile = function() {
    const name = document.getElementById('nameInput').value;
    const weight = document.getElementById('weightInput').value;
    const age = document.getElementById('ageInput').value;
    const goals = document.getElementById('goalsInput').value;

    // Save to Firebase
    set(ref(db, 'Input'), {
        name: name,
        weight: weight,
        age: age,
        goals: goals
    })
    .then(() => {
        alert('Profile updated successfully!');
    })
    .catch((error) => {
        alert('Error updating profile: ' + error);
    });


    // Update the display on the profile page
    document.getElementById('nameDisplay').textContent = name || 'Name';
    document.getElementById('weightDisplay').textContent = weight ? weight + ' kg' : '... kg';
    document.getElementById('ageDisplay').textContent = age ? age + ' years' : '... years';
    document.getElementById('goalsDisplay').textContent = goals || '...';

    // Hide the form after updating
    document.getElementById('profileFormContainer').style.display = 'none';
};


// Handle profile picture change
document.getElementById('profilePicInput').addEventListener('change', function (event) {
    const reader = new FileReader();
    reader.onload = function () {
        document.getElementById('profilePic').src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
});

// Fetch initial profile data on page load
window.onload = fetchData;
fetchData().then(() => {
    startMqtt();
});