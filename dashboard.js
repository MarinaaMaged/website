
// Create Charts for each metric
let waterIntakeChart = createChart('waterIntakeChart', 'Water Intake');
let heartRateChart = createChart('heartRateChart', 'Heart Rate');
let temperatureChart = createChart('temperatureChart', 'Temperature');
let caloriesBurnedChart = createChart('caloriesBurnedChart', 'Calories Burned');
let spO2Chart = createChart('spO2Chart', 'Oxygen Saturation');
let humidityChart = createChart('humidityChart', 'Humidity');
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
    document.getElementById('waterIntake').textContent = data.calc.waterIntake + " ml/hr";
    document.getElementById('heartRate').textContent = data.Sensor.heartRate + " BPM";
    document.getElementById('temperature').textContent = data.Sensor.temperature + " °C";
    document.getElementById('caloriesBurned').textContent = data.calc.kcalPerHour + " Kcal/hr";
    document.getElementById('spO2').textContent = data.Sensor.spO2 + "%";
    document.getElementById('humidity').textContent = data.Sensor.humidity + "%";
    // Add data to the charts (assumed to be in real-time with timestamp labels)
    updateChart(waterIntakeChart, data.waterIntake);
    updateChart(heartRateChart, data.Sensor.heartRate);
    updateChart(temperatureChart, data.Sensor.temperature);
    updateChart(caloriesBurnedChart, data.calc.kcalPerHour);
    updateChart(spO2Chart, data.Sensor.spO2);
    updateChart(humidityChart, data.Sensor.humidity);
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

async function fetchData() {
    try {
        const response = await fetch('http://localhost:5000/get_data');
        const data = await response.json();
        console.log("Fetched data:", data); // Log data for debugging
        if (response.ok) {
            updateDashboard(data); // Update dashboard with fetched data
        } else {
            console.error("Error fetching data:", data.error);
        }
    } catch (error) {
        console.error("Error fetching data:", error);
    }
}
setInterval(fetchData, 5000);

// Display current date
const dateElement = document.getElementById('date');
const today = new Date();
dateElement.textContent = today.toDateString();

// Call fetchData to start fetching data from Flask
fetchData();
