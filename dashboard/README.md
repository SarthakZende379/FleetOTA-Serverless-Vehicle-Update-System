# FleetOTA Dashboard

## Overview
Interactive web dashboard for real-time fleet monitoring and OTA update management visualization.

## Features

### 📊 Live Statistics
- Total vehicles in fleet
- Online/offline vehicle count
- Update eligible vehicles
- Up-to-date vehicles

### 📈 Visual Charts
1. **Fleet Status Distribution** (Doughnut Chart)
   - Online vs Offline vs Updating vehicles
   
2. **Firmware Version Distribution** (Bar Chart)
   - Count of vehicles per firmware version
   
3. **Average Battery Level** (Line Chart)
   - Historical battery trends
   - 12-hour view with auto-scroll
   
4. **Update Campaign Progress** (Horizontal Bar Chart)
   - Eligible, In Progress, Completed, Failed updates

### 📋 Vehicle Table
- Recent vehicle telemetry (top 20 vehicles)
- Real-time status badges
- Battery level indicators with visual bars
- Signal strength metrics
- Firmware version tracking
- Last update timestamp

## Technology Stack

- **HTML5** - Structure
- **CSS3** - Styling with animations
- **JavaScript** - Logic and interactivity
- **Chart.js 4.4.0** - Data visualization
- **Responsive Design** - Works on desktop, tablet, mobile

## How to Use

### Option 1: Open Locally (Simplest)

```bash
# Navigate to dashboard directory
cd dashboard

# Open in browser
open index.html
# OR
python3 -m http.server 8000
# Then visit: http://localhost:8000
```

### Option 2: Deploy to S3 Static Website

```bash
# Create S3 bucket for website
aws s3 mb s3://fleetota-dashboard

# Enable static website hosting
aws s3 website s3://fleetota-dashboard --index-document index.html

# Upload dashboard files
aws s3 sync . s3://fleetota-dashboard --acl public-read

# Get website URL
echo "http://fleetota-dashboard.s3-website-us-east-1.amazonaws.com"
```

### Option 3: Deploy to GitHub Pages

```bash
# In your repository settings:
# Settings → Pages → Source → main branch → /dashboard folder
# Your dashboard will be available at:
# https://YOUR_USERNAME.github.io/FleetOTA-Serverless-Vehicle-Update-System/
```

## Dashboard Sections Explained

### 1. Stats Cards (Top Row)
Four key metrics displayed prominently:
- **Total Vehicles**: Full fleet size
- **Vehicles Online**: Currently connected vehicles
- **Update Eligible**: Ready for firmware update
- **Up to Date**: Already on latest firmware

The "Update Eligible" card pulses to draw attention.

### 2. Charts (Middle Section)

**Fleet Status Distribution:**
- Visual breakdown of online/offline/updating vehicles
- Doughnut chart with percentages
- Color coded: Green (online), Red (offline), Yellow (updating)

**Firmware Version Distribution:**
- Bar chart showing vehicles per firmware version
- Helps identify how many vehicles need updates
- Sorted by version number

**Average Battery Level:**
- Line chart showing battery trends over 12 hours
- Auto-updates every 30 seconds
- Smooth curve with area fill

**Update Campaign Progress:**
- Horizontal bar chart
- Shows update pipeline: Eligible → In Progress → Completed
- Includes failed update count

### 3. Vehicle Table (Bottom Section)
Detailed view of recent vehicle telemetry:
- **Vehicle ID**: Unique identifier
- **VIN**: Vehicle Identification Number (17 chars)
- **Status**: Badge showing online/offline/updating
- **Battery**: Visual bar + percentage
- **Firmware**: Current version
- **Signal**: Network strength (dBm) + quality indicator
- **Last Update**: Relative time (e.g., "5m ago")

## Customization

### Update Refresh Interval
Edit `app.js` line ~60:
```javascript
// Change from 30 seconds to 10 seconds
setInterval(refreshData, 10000);
```

### Change Color Scheme
Edit `styles.css` variables:
```css
:root {
    --primary-color: #2563eb;  /* Change to your brand color */
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
}
```

### Show More Vehicles in Table
Edit `app.js` line ~280:
```javascript
// Change from 20 to 50
const displayVehicles = fleetData.vehicles.slice(0, 50);
```

## Integration with Real AWS Data

Currently, the dashboard uses **simulated data**. To connect to real CloudWatch metrics:

### Step 1: Install AWS SDK
```html
<!-- Add to index.html before app.js -->
<script src="https://sdk.amazonaws.com/js/aws-sdk-2.1000.0.min.js"></script>
```

### Step 2: Configure AWS Credentials
```javascript
// Add to app.js
AWS.config.region = 'us-east-1';
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'YOUR_IDENTITY_POOL_ID'
});
```

### Step 3: Fetch CloudWatch Metrics
```javascript
async function fetchCloudWatchMetrics() {
    const cloudwatch = new AWS.CloudWatch();
    
    const params = {
        Namespace: 'FleetOTA',
        MetricName: 'VehiclesOnline',
        StartTime: new Date(Date.now() - 3600000),
        EndTime: new Date(),
        Period: 300,
        Statistics: ['Average']
    };
    
    const data = await cloudwatch.getMetricStatistics(params).promise();
    // Process data and update charts
}
```

## Performance Optimization

- **Lazy Loading**: Charts initialize only when visible
- **Data Caching**: Vehicle data cached in memory
- **Throttled Updates**: Auto-refresh limited to 30s
- **Efficient Rendering**: Only updates changed elements

## Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome | ✅ Latest |
| Firefox | ✅ Latest |
| Safari | ✅ Latest |
| Edge | ✅ Latest |
| Mobile | ✅ Responsive |

## Troubleshooting

### Charts not displaying
- Check browser console for errors
- Verify Chart.js CDN is loaded
- Clear browser cache

### Data not updating
- Check `app.js` is loaded
- Look for JavaScript errors in console
- Verify auto-refresh interval is set

### Styling issues
- Ensure `styles.css` is linked correctly
- Check for CSS conflicts
- Try hard refresh (Ctrl+F5)

## Screenshots

### Desktop View
![Dashboard Desktop](../docs/screenshots/dashboard-desktop.png)

### Mobile View
![Dashboard Mobile](../docs/screenshots/dashboard-mobile.png)

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] AWS CloudWatch integration
- [ ] Export data to CSV
- [ ] Dark mode toggle
- [ ] Vehicle detail modal
- [ ] Update campaign management
- [ ] Alert notifications
- [ ] Historical data playback
- [ ] Custom date range filters
- [ ] Multi-fleet support



**Demo flow:**
1. Show live stats updating
2. Explain each chart's purpose
3. Demonstrate responsive design
4. Discuss AWS integration possibilities

## License
MIT License - See LICENSE file

## Author
**Sarthak Zende**  
MS Computer Science Student  
