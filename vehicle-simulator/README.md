# Vehicle Simulator

Realistic telemetry generator for FleetOTA system simulating 100+ connected vehicles.

## 📋 Overview

This module generates authentic vehicle telemetry data mimicking real-world automotive systems. Each simulated vehicle has:

- **Unique VIN** (Vehicle Identification Number) with proper check digit
- **GPS tracking** with realistic movement patterns
- **Battery monitoring** with charge/discharge simulation
- **Connectivity status** (4G/5G/WiFi/Satellite)
- **Firmware version** tracking
- **Diagnostic data** and health metrics

## 🏗️ Architecture

```
Vehicle Generator
    ↓
VINGenerator → Generates SAE J853 compliant VINs
    ↓
GPSSimulator → Simulates movement patterns
    ↓
Vehicle (100 instances) → Generate telemetry
    ↓
FleetSimulator → Orchestrates uploads
    ↓
AWS S3 → Stores telemetry data
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install boto3

# Configure
cp config.py.example config.py
# Edit config.py with your S3 bucket name

# Run with 5 test vehicles
python vehicle_generator.py --vehicles 5 --duration 2 --interval 30

# Full production run
python vehicle_generator.py --vehicles 100 --duration 60 --interval 60
```

## 📊 Sample Telemetry Output

```json
{
  "vehicle_id": 42,
  "vin": "5YJSA1E14MF123456",
  "timestamp": "2025-09-29T14:30:45.123456",
  "model": "Model-S",
  "year": 2024,
  "gps": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "speed_kmh": 65.5,
    "heading": 180
  },
  "battery": {
    "percent": 85.5,
    "health": 95.2,
    "voltage": 385.4,
    "temperature_celsius": 28.3
  },
  "connectivity": {
    "type": "5G",
    "signal_strength_dbm": -65,
    "data_usage_mb": 245.67,
    "connected": true
  },
  "status": "online",
  "odometer_km": 15234.5,
  "firmware": {
    "current_version": "1.3.1",
    "update_available": true,
    "update_downloaded": false,
    "last_update_check": "2025-09-29T14:00:00"
  },
  "diagnostics": {
    "error_codes": [],
    "warnings": ["WEAK_SIGNAL"],
    "health_score": 92.5
  }
}
```

## 🎛️ Configuration

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--vehicles` | 100 | Number of vehicles to simulate |
| `--duration` | 60 | Simulation duration (minutes) |
| `--interval` | 60 | Telemetry interval (seconds) |
| `--bucket` | fleetota-telemetry | S3 bucket name |
| `--region` | us-east-1 | AWS region |
| `--log-level` | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

### config.py Settings

```python
# Fleet Configuration
VEHICLE_COUNT = 100
TELEMETRY_INTERVAL = 60

# Firmware Versions
FIRMWARE_VERSIONS = ['1.2.0', '1.2.1', '1.3.0', '1.3.1', '1.4.0', '2.0.0']

# Battery Simulation
BATTERY_DRAIN_RATE_MIN = 0.1  # % per minute
BATTERY_DRAIN_RATE_MAX = 0.5

# GPS Settings
GPS_SPEED_MIN_KMH = 0
GPS_SPEED_MAX_KMH = 120

# City Distribution
CITY_CENTERS = {
    'San Francisco': (37.7749, -122.4194),
    'New York': (40.7128, -74.0060),
    # ... more cities
}
```

## 🔧 Components

### 1. VINGenerator

Generates realistic 17-character VINs following SAE J853 standard:

```python
vin = VINGenerator.generate(manufacturer='TESLA')
# Output: 5YJSA1E14MF123456
#         ^
#         Check digit (position 9)
```

**Features:**
- Proper WMI (World Manufacturer Identifier) codes
- Modulo 11 check digit calculation
- Year and plant code encoding
- Serial number generation

### 2. GPSSimulator

Simulates realistic vehicle movement:

```python
gps = GPSSimulator(initial_lat=37.7749, initial_lon=-122.4194)
lat, lon = gps.update_position(time_elapsed_seconds=60)
```

**Features:**
- Random walk with speed persistence
- Urban/highway speed simulation (0-120 km/h)
- Geographic constraints (valid lat/lon bounds)
- Distance-based position updates

### 3. Vehicle

Represents individual vehicle with full state:

```python
vehicle = Vehicle(vehicle_id=1)
telemetry = vehicle.generate_telemetry()
```

**Features:**
- Battery drain simulation with charging
- Status transitions (online/offline/updating)
- Connectivity type changes (4G/5G/WiFi/Satellite)
- Signal strength fluctuation
- Odometer tracking
- Warning generation (low battery, weak signal)

### 4. FleetSimulator

Orchestrates entire fleet:

```python
simulator = FleetSimulator(num_vehicles=100, s3_bucket='my-bucket')
simulator.run_simulation(duration_minutes=60, interval_seconds=60)
```

**Features:**
- Concurrent vehicle management
- S3 upload with retry logic
- Statistics tracking
- Graceful shutdown (Ctrl+C)
- Summary reporting

## 📈 Performance

| Metric | Value |
|--------|-------|
| Vehicles | 100 |
| Interval | 60s |
| Telemetry/Hour | 6,000 |
| Data Size/Upload | ~1-2 KB |
| Total Data/Hour | ~12 MB |
| S3 Requests/Hour | 6,000 PUT |
| Memory Usage | ~50 MB |
| CPU Usage | <5% |

## 🧪 Testing

### Unit Tests

```bash
cd tests/
python -m pytest test_vehicle_generator.py -v
```

### Integration Test

```bash
# Test with real S3
python vehicle_generator.py --vehicles 5 --duration 1 --interval 30

# Verify uploads
aws s3 ls s3://YOUR_BUCKET/telemetry/ --recursive
```

### Stress Test

```bash
# 1000 vehicles (may exceed Free Tier)
python vehicle_generator.py --vehicles 1000 --duration 5 --interval 60
```

## 🐛 Troubleshooting

### No data in S3

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check bucket exists
aws s3 ls | grep fleetota

# Verify bucket permissions
aws s3api get-bucket-policy --bucket YOUR_BUCKET
```

### High error rate

```bash
# Run with DEBUG logging
python vehicle_generator.py --log-level DEBUG

# Check network connectivity
ping s3.amazonaws.com

# Increase retry attempts in config.py
MAX_RETRIES = 5
```

### Slow performance

```bash
# Reduce vehicle count
python vehicle_generator.py --vehicles 50

# Increase interval
python vehicle_generator.py --interval 120

# Use faster AWS region
python vehicle_generator.py --region us-west-2
```

## 📊 Monitoring

### View Live Stats

```bash
# In separate terminal
tail -f vehicle_simulator.log | grep "complete:"
```

### S3 Upload Rate

```bash
# Count uploads per minute
watch -n 60 'aws s3 ls s3://YOUR_BUCKET/telemetry/ --recursive | wc -l'
```

### CloudWatch Metrics (after Lambda setup)

```bash
aws cloudwatch get-metric-statistics \
  --namespace FleetOTA \
  --metric-name VehiclesOnline \
  --start-time 2025-09-29T00:00:00Z \
  --end-time 2025-09-29T23:59:59Z \
  --period 3600 \
  --statistics Average
```

## 🔐 Security Best Practices

1. **Never commit credentials**
   ```bash
   # Add to .gitignore
   echo "*.env" >> .gitignore
   echo "config.json" >> .gitignore
   ```

2. **Use IAM roles** (when running on EC2)
   ```python
   # No need to specify credentials
   s3_client = boto3.client('s3')
   ```

3. **Encrypt S3 bucket**
   ```bash
   aws s3api put-bucket-encryption \
     --bucket YOUR_BUCKET \
     --server-side-encryption-configuration '{
       "Rules": [{
         "ApplyServerSideEncryptionByDefault": {
           "SSEAlgorithm": "AES256"
         }
       }]
     }'
   ```

## 💡 Advanced Usage

### Custom City Distribution

```python
# In config.py
CITY_CENTERS['Detroit'] = (42.3314, -83.0458)
CITY_CENTERS['Tokyo'] = (35.6762, 139.6503)
```

### Simulate Specific Scenario

```python
# Create vehicle with specific state
vehicle = Vehicle(vehicle_id=999)
vehicle.firmware_version = '1.2.0'  # Old version
vehicle.battery_percent = 10  # Low battery
vehicle.connectivity = ConnectivityType.LTE  # Poor connectivity
vehicle.status = VehicleStatus.ERROR  # Error state

telemetry = vehicle.generate_telemetry()
```

### Batch Upload

```python
# Upload multiple vehicles' data at once
batch = [v.generate_telemetry() for v in vehicles]
# Process batch...
```

## 🎓 Learning Resources

- [SAE J853 VIN Standard](https://www.iso.org/standard/52200.html)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Automotive Telematics](https://en.wikipedia.org/wiki/Telematics)

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

[Your Name] - MS Computer Science Student  
Built for KPIT Technologies cloud operations role application

---

**Next Steps**: After generating telemetry, proceed to Lambda function setup to process this data!