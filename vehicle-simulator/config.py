"""
FleetOTA Configuration
======================
Central configuration file for the vehicle simulator and telemetry system.

Modify these settings based on your AWS setup and simulation requirements.
"""

import os
from typing import Dict, List

# ============================================================================
# AWS Configuration
# ============================================================================

# S3 Bucket Configuration
# IMPORTANT: Change this to your unique bucket name
S3_BUCKET = os.getenv('FLEETOTA_S3_BUCKET', 'fleetota-telemetry-YOUR_UNIQUE_ID')

# AWS Region
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# S3 Key Prefix for organizing telemetry data
S3_TELEMETRY_PREFIX = 'telemetry'

# ============================================================================
# Fleet Simulation Settings
# ============================================================================

# Number of vehicles in the simulated fleet
VEHICLE_COUNT = 100

# Telemetry generation interval (seconds)
# Realistic values: 30-300 seconds
TELEMETRY_INTERVAL = 60

# Simulation duration (minutes)
# Set to 0 for continuous operation
SIMULATION_DURATION = 60

# ============================================================================
# Vehicle Configuration
# ============================================================================

# Available firmware versions (oldest to newest)
FIRMWARE_VERSIONS: List[str] = [
    '1.2.0',   # Legacy version
    '1.2.1',   # Security patch
    '1.3.0',   # Minor update
    '1.3.1',   # Bug fixes
    '1.4.0',   # Current stable
    '2.0.0'    # Latest release
]

# Initial firmware distribution (must sum to 1.0)
FIRMWARE_DISTRIBUTION: Dict[str, float] = {
    '1.2.0': 0.10,  # 10% on oldest version
    '1.2.1': 0.15,  # 15%
    '1.3.0': 0.25,  # 25%
    '1.3.1': 0.30,  # 30%
    '1.4.0': 0.15,  # 15%
    '2.0.0': 0.05   # 5% early adopters
}

# Vehicle models available in fleet
VEHICLE_MODELS: List[str] = [
    'Model-S',
    'Model-3',
    'Model-X',
    'Model-Y',
    'Cybertruck'
]

# Model year range
VEHICLE_YEAR_MIN = 2020
VEHICLE_YEAR_MAX = 2025

# ============================================================================
# Telemetry Parameters
# ============================================================================

# Battery simulation
BATTERY_DRAIN_RATE_MIN = 0.1   # % per minute (minimum)
BATTERY_DRAIN_RATE_MAX = 0.5   # % per minute (maximum)
BATTERY_LOW_THRESHOLD = 15     # % (warning threshold)
BATTERY_CRITICAL_THRESHOLD = 5 # % (critical threshold)

# GPS simulation
GPS_UPDATE_ENABLED = True
GPS_SPEED_MIN_KMH = 0          # Minimum speed (parked)
GPS_SPEED_MAX_KMH = 120        # Maximum speed (highway)

# Connectivity simulation
CONNECTIVITY_TYPES: List[str] = ['4G_LTE', '5G', 'WiFi', 'Satellite']
SIGNAL_STRENGTH_MIN_DBM = -90  # Weak signal
SIGNAL_STRENGTH_MAX_DBM = -40  # Strong signal

# Vehicle status probabilities
PROBABILITY_GO_OFFLINE = 0.02   # 2% chance per interval
PROBABILITY_COME_ONLINE = 0.30  # 30% chance to reconnect
PROBABILITY_UPDATE_AVAILABLE = 0.30  # 30% of fleet has updates

# ============================================================================
# Logging Configuration
# ============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Log file path
LOG_FILE = 'vehicle_simulator.log'

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# CloudWatch Metrics Configuration
# ============================================================================

# CloudWatch namespace for custom metrics
CLOUDWATCH_NAMESPACE = 'FleetOTA'

# Metrics to publish
PUBLISH_METRICS = True

# Metric publishing interval (seconds)
METRIC_PUBLISH_INTERVAL = 60

# ============================================================================
# Geographic Distribution
# ============================================================================

# Major cities for vehicle distribution (name: (lat, lon))
CITY_CENTERS: Dict[str, tuple] = {
    'San Francisco': (37.7749, -122.4194),
    'Los Angeles': (34.0522, -118.2437),
    'Chicago': (41.8781, -87.6298),
    'New York': (40.7128, -74.0060),
    'Austin': (30.2672, -97.7431),
    'Seattle': (47.6062, -122.3321),
    'Detroit': (42.3314, -83.0458),
    'Boston': (42.3601, -71.0589),
    'Miami': (25.7617, -80.1918),
    'Denver': (39.7392, -104.9903)
}

# Radius for vehicle distribution around cities (km)
CITY_DISTRIBUTION_RADIUS_KM = 50

# ============================================================================
# Error Simulation (for testing resilience)
# ============================================================================

# Simulate upload failures for testing Lambda retry logic
SIMULATE_UPLOAD_FAILURES = False
UPLOAD_FAILURE_RATE = 0.05  # 5% failure rate

# Simulate malformed data for error handling tests
SIMULATE_MALFORMED_DATA = False
MALFORMED_DATA_RATE = 0.02  # 2% malformed rate

# ============================================================================
# Performance Settings
# ============================================================================

# Maximum concurrent S3 uploads (threading)
MAX_CONCURRENT_UPLOADS = 10

# S3 request timeout (seconds)
S3_TIMEOUT = 30

# Retry configuration for S3 uploads
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2

# ============================================================================
# Development / Testing Settings
# ============================================================================

# Enable debug mode (verbose logging, additional validation)
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# DynamoDB table for vehicle state (optional, for future enhancement)
DYNAMODB_TABLE = os.getenv('FLEETOTA_DYNAMODB_TABLE', 'fleetota-vehicle-state')

# SNS topic for alerts (optional, for future enhancement)
SNS_ALERT_TOPIC = os.getenv('FLEETOTA_SNS_TOPIC', '')

# ============================================================================
# Validation
# ============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if S3_BUCKET == 'fleetota-telemetry-YOUR_UNIQUE_ID':
        errors.append("S3_BUCKET must be changed from default value")
    
    if not (1 <= VEHICLE_COUNT <= 10000):
        errors.append("VEHICLE_COUNT must be between 1 and 10000")
    
    if not (10 <= TELEMETRY_INTERVAL <= 3600):
        errors.append("TELEMETRY_INTERVAL must be between 10 and 3600 seconds")
    
    if abs(sum(FIRMWARE_DISTRIBUTION.values()) - 1.0) > 0.01:
        errors.append("FIRMWARE_DISTRIBUTION must sum to 1.0")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


# Validate on import (can be disabled for testing)
if __name__ != '__main__':
    try:
        validate_config()
    except ValueError as e:
        print(f"Warning: {e}")


if __name__ == '__main__':
    print("FleetOTA Configuration")
    print("=" * 70)
    print(f"S3 Bucket:        {S3_BUCKET}")
    print(f"AWS Region:       {AWS_REGION}")
    print(f"Vehicle Count:    {VEHICLE_COUNT}")
    print(f"Interval:         {TELEMETRY_INTERVAL}s")
    print(f"Duration:         {SIMULATION_DURATION}m")
    print(f"Firmware Versions: {len(FIRMWARE_VERSIONS)}")
    print(f"City Centers:     {len(CITY_CENTERS)}")
    print("=" * 70)
    
    try:
        validate_config()
        print("✓ Configuration valid")
    except ValueError as e:
        print(f"✗ Configuration invalid:\n{e}")