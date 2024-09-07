// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBBBkTMKdegGRfGMRfWn_dTYR5S4EPp--g",
    authDomain: "YOUR_AUTH_DOMAIN",
    databaseURL: "https://iot-workout-tracker-default-rtdb.europe-west1.firebasedatabase.app/" ,
    projectId: "iot-workout-tracker",
    //storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "848259868418",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = firebase.initializeApp(firebaseConfig);
const database = firebase.database();

// Create Charts for each metric
//let activeMinutesChart = createChart('activeMinutesChart', 'Active Minutes');
//let caloriesBurnedChart = createChart('caloriesBurnedChart', 'Calories Burned');
//let stepsTakenChart = createChart('stepsTakenChart', 'Steps Taken');
let waterIntakeChart = createChart('waterIntakeChart', 'Water Intake');
let heartRateChart = createChart('heartRateChart', 'Heart Rate');
let temperatureChart = createChart('temperatureChart', 'Temperature');

// Function to create a chart
function createChart(canvasId, label) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Time or days
            datasets: [{
                label: label,
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    beginAtZero: true
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Function to update the dashboard and charts
function updateDashboard(data) {
    // Update text content
    //document.getElementById('activeMinutes').textContent = data.activeMinutes + " Min";
    //document.getElementById('caloriesBurned').textContent = data.caloriesBurned + " Kcal";
    //document.getElementById('stepsTaken').textContent = data.stepsTaken + " Steps";
    document.getElementById('waterIntake').textContent = data.waterIntake + "/10 Glasses";
    document.getElementById('heartRate').textContent = data.heartRate + " BPM";
    document.getElementById('temperature').textContent = data.temperature + " °C";

    // Add data to the charts (assumed to be in real-time with timestamp labels)
    //updateChart(activeMinutesChart, data.activeMinutes);
    //updateChart(caloriesBurnedChart, data.caloriesBurned);
    //updateChart(stepsTakenChart, data.stepsTaken);
    updateChart(waterIntakeChart, data.waterIntake);
    updateChart(heartRateChart, data.heartRate);
    updateChart(temperatureChart, data.temperature);
}

// Function to update chart data
function updateChart(chart, newData) {
    const timestamp = new Date().toLocaleTimeString(); // Use this for real-time data
    chart.data.labels.push(timestamp);
    chart.data.datasets[0].data.push(newData);
    
    // Keep only the last 10 data points to avoid overloading the chart
    if (chart.data.labels.length > 10) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

// Fetch data from Firebase Realtime Database
const userId = "userId_123"; // Replace with the actual user ID
const userRef = firebase.database().ref('users/' + userId);

// Listen for real-time updates from Firebase
userRef.on('value', (snapshot) => {
    const data = snapshot.val();
    updateDashboard(data);
});

// Display current date
const dateElement = document.getElementById('date');
const today = new Date();
dateElement.textContent = today.toDateString();