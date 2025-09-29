/**
 * FleetOTA Dashboard JavaScript
 * Simulates real-time fleet monitoring with Chart.js visualizations
 * 
 * Author: Sarthak Zende
 */

// Sample data storage (simulating real data)
let fleetData = {
    totalVehicles: 100,
    onlineVehicles: 75,
    updateEligible: 35,
    upToDate: 20,
    vehicles: []
};

// Chart instances
let fleetStatusChart;
let firmwareChart;
let batteryChart;
let updateProgressChart;

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('FleetOTA Dashboard Initializing...');
    
    // Generate sample vehicle data
    generateSampleVehicleData();
    
    // Update stats
    updateStatCards();
    
    // Initialize charts
    initializeCharts();
    
    // Populate vehicle table
    populateVehicleTable();
    
    // Update timestamp
    updateTimestamp();
    
    // Set up refresh button
    document.getElementById('refresh-btn').addEventListener('click', refreshData);
    
    // Auto-refresh every 30 seconds
    setInterval(refreshData, 30000);
    
    console.log('Dashboard initialized successfully!');
});

/**
 * Generate sample vehicle data for demonstration
 */
function generateSampleVehicleData() {
    const statuses = ['online', 'offline', 'updating'];
    const firmwareVersions = ['1.2.0', '1.2.1', '1.3.0', '1.3.1', '1.4.0', '2.0.0'];
    const models = ['Model-S', 'Model-3', 'Model-X', 'Model-Y', 'Cybertruck'];
    
    fleetData.vehicles = [];
    
    for (let i = 1; i <= fleetData.totalVehicles; i++) {
        const status = statuses[Math.floor(Math.random() * statuses.length)];
        const batteryPercent = Math.floor(Math.random() * 80) + 20;
        const firmwareVersion = firmwareVersions[Math.floor(Math.random() * firmwareVersions.length)];
        
        fleetData.vehicles.push({
            id: i,
            vin: generateVIN(),
            model: models[Math.floor(Math.random() * models.length)],
            status: status,
            battery: batteryPercent,
            firmware: firmwareVersion,
            signal: -Math.floor(Math.random() * 50) - 40, // -40 to -90 dBm
            lastUpdate: new Date(Date.now() - Math.random() * 3600000).toISOString()
        });
    }
}

/**
 * Generate random VIN
 */
function generateVIN() {
    const chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789';
    let vin = '5YJ';
    for (let i = 0; i < 14; i++) {
        vin += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return vin;
}

/**
 * Update stat cards
 */
function updateStatCards() {
    document.getElementById('total-vehicles').textContent = fleetData.totalVehicles;
    document.getElementById('vehicles-online').textContent = fleetData.onlineVehicles;
    document.getElementById('update-eligible').textContent = fleetData.updateEligible;
    document.getElementById('up-to-date').textContent = fleetData.upToDate;
}

/**
 * Initialize all charts
 */
function initializeCharts() {
    initFleetStatusChart();
    initFirmwareChart();
    initBatteryChart();
    initUpdateProgressChart();
}

/**
 * Fleet Status Chart (Doughnut)
 */
function initFleetStatusChart() {
    const ctx = document.getElementById('fleetStatusChart').getContext('2d');
    
    const online = fleetData.vehicles.filter(v => v.status === 'online').length;
    const offline = fleetData.vehicles.filter(v => v.status === 'offline').length;
    const updating = fleetData.vehicles.filter(v => v.status === 'updating').length;
    
    fleetStatusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Online', 'Offline', 'Updating'],
            datasets: [{
                data: [online, offline, updating],
                backgroundColor: [
                    '#10b981', // Green
                    '#ef4444', // Red
                    '#f59e0b'  // Yellow
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Firmware Version Chart (Bar)
 */
function initFirmwareChart() {
    const ctx = document.getElementById('firmwareChart').getContext('2d');
    
    // Count vehicles by firmware version
    const firmwareCounts = {};
    fleetData.vehicles.forEach(vehicle => {
        firmwareCounts[vehicle.firmware] = (firmwareCounts[vehicle.firmware] || 0) + 1;
    });
    
    const labels = Object.keys(firmwareCounts).sort();
    const data = labels.map(version => firmwareCounts[version]);
    
    firmwareChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Vehicles',
                data: data,
                backgroundColor: '#2563eb',
                borderColor: '#1e40af',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Battery Level Chart (Line)
 */
function initBatteryChart() {
    const ctx = document.getElementById('batteryChart').getContext('2d');
    
    // Calculate average battery by status
    const onlineVehicles = fleetData.vehicles.filter(v => v.status === 'online');
    const avgBattery = onlineVehicles.reduce((sum, v) => sum + v.battery, 0) / onlineVehicles.length;
    
    // Simulate historical data
    const labels = [];
    const data = [];
    for (let i = 11; i >= 0; i--) {
        const date = new Date();
        date.setHours(date.getHours() - i);
        labels.push(date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        data.push(avgBattery + (Math.random() - 0.5) * 10);
    }
    
    batteryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Battery %',
                data: data,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 40,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Update Progress Chart (Horizontal Bar)
 */
function initUpdateProgressChart() {
    const ctx = document.getElementById('updateProgressChart').getContext('2d');
    
    updateProgressChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Eligible', 'In Progress', 'Completed', 'Failed'],
            datasets: [{
                label: 'Vehicles',
                data: [35, 5, 20, 2],
                backgroundColor: [
                    '#f59e0b', // Warning - Eligible
                    '#3b82f6', // Blue - In Progress
                    '#10b981', // Green - Completed
                    '#ef4444'  // Red - Failed
                ],
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Populate vehicle table
 */
function populateVehicleTable() {
    const tbody = document.getElementById('vehicle-table-body');
    tbody.innerHTML = '';
    
    // Show only first 20 vehicles
    const displayVehicles = fleetData.vehicles.slice(0, 20);
    
    displayVehicles.forEach(vehicle => {
        const row = document.createElement('tr');
        
        // Status badge
        const statusClass = `status-${vehicle.status}`;
        const statusBadge = `<span class="status-badge ${statusClass}">${vehicle.status.toUpperCase()}</span>`;
        
        // Battery indicator
        const batteryColor = vehicle.battery < 30 ? 'low' : vehicle.battery < 60 ? 'medium' : 'high';
        const batteryIndicator = `
            <div class="battery-indicator">
                <span>${vehicle.battery}%</span>
                <div class="battery-bar">
                    <div class="battery-fill ${batteryColor}" style="width: ${vehicle.battery}%"></div>
                </div>
            </div>
        `;
        
        // Signal strength
        const signalText = vehicle.signal > -60 ? 'Excellent' : 
                          vehicle.signal > -70 ? 'Good' : 
                          vehicle.signal > -80 ? 'Fair' : 'Poor';
        
        // Last update time
        const lastUpdate = new Date(vehicle.lastUpdate);
        const timeAgo = getTimeAgo(lastUpdate);
        
        row.innerHTML = `
            <td><strong>#${vehicle.id}</strong></td>
            <td><code>${vehicle.vin}</code></td>
            <td>${statusBadge}</td>
            <td>${batteryIndicator}</td>
            <td><strong>${vehicle.firmware}</strong></td>
            <td>${vehicle.signal} dBm (${signalText})</td>
            <td>${timeAgo}</td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Get time ago string
 */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

/**
 * Update timestamp
 */
function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US');
    document.getElementById('last-update-time').textContent = timeString;
}

/**
 * Refresh data (simulate real-time updates)
 */
function refreshData() {
    console.log('Refreshing dashboard data...');
    
    // Slightly modify data to simulate changes
    fleetData.vehicles.forEach(vehicle => {
        // Random status changes
        if (Math.random() < 0.05) {
            const statuses = ['online', 'offline'];
            vehicle.status = statuses[Math.floor(Math.random() * statuses.length)];
        }
        
        // Battery drain/charge
        if (vehicle.status === 'online') {
            vehicle.battery = Math.max(10, vehicle.battery - Math.random() * 2);
        } else {
            vehicle.battery = Math.min(100, vehicle.battery + Math.random() * 5);
        }
        
        // Update timestamp
        vehicle.lastUpdate = new Date().toISOString();
    });
    
    // Recalculate stats
    fleetData.onlineVehicles = fleetData.vehicles.filter(v => v.status === 'online').length;
    
    // Update UI
    updateStatCards();
    updateCharts();
    populateVehicleTable();
    updateTimestamp();
    
    console.log('Dashboard refreshed!');
}

/**
 * Update all charts with new data
 */
function updateCharts() {
    // Update fleet status chart
    const online = fleetData.vehicles.filter(v => v.status === 'online').length;
    const offline = fleetData.vehicles.filter(v => v.status === 'offline').length;
    const updating = fleetData.vehicles.filter(v => v.status === 'updating').length;
    
    fleetStatusChart.data.datasets[0].data = [online, offline, updating];
    fleetStatusChart.update();
    
    // Update battery chart (add new data point)
    const onlineVehicles = fleetData.vehicles.filter(v => v.status === 'online');
    const avgBattery = onlineVehicles.reduce((sum, v) => sum + v.battery, 0) / onlineVehicles.length;
    
    batteryChart.data.labels.shift();
    batteryChart.data.labels.push(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
    batteryChart.data.datasets[0].data.shift();
    batteryChart.data.datasets[0].data.push(avgBattery);
    batteryChart.update();
}

console.log('FleetOTA Dashboard Script Loaded');