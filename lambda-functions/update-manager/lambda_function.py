"""
FleetOTA Update Manager Lambda Function
========================================
Manages OTA firmware updates for vehicle fleet.

Trigger: CloudWatch EventBridge (scheduled every 5 minutes)
         OR API Gateway (manual trigger)
Output: Update campaign metrics to CloudWatch

Author: Sarthak Zende
"""

import json
import boto3
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# Initialize AWS clients
s3_client = boto3.client('s3')
cloudwatch_client = boto3.client('cloudwatch')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Update configuration
LATEST_FIRMWARE_VERSION = "2.0.0"
MINIMUM_BATTERY_PERCENT = 50  # Minimum battery to start update
UPDATE_PRIORITY_VERSIONS = ["1.2.0", "1.2.1"]  # Critical old versions


def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    Args:
        event: EventBridge scheduled event or manual trigger
        context: Lambda context object
        
    Returns:
        dict: Response with update statistics
    """
    
    logger.info(f"Update Manager started at {datetime.now()}")
    
    try:
        # Get recent telemetry from S3
        bucket_name = get_bucket_name()
        telemetry_files = get_recent_telemetry(bucket_name)
        
        logger.info(f"Found {len(telemetry_files)} telemetry files to analyze")
        
        # Analyze fleet and determine update eligibility
        fleet_status = analyze_fleet(bucket_name, telemetry_files)
        
        # Publish update metrics
        publish_update_metrics(fleet_status)
        
        # Log summary
        log_summary(fleet_status)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Update analysis complete',
                'total_vehicles': fleet_status['total_vehicles'],
                'update_eligible': fleet_status['update_eligible'],
                'update_in_progress': fleet_status['update_in_progress'],
                'latest_version': LATEST_FIRMWARE_VERSION
            })
        }
        
    except Exception as e:
        logger.error(f"Error in update manager: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }


def get_bucket_name():
    """
    Get S3 bucket name from environment or use default.
    
    Returns:
        str: S3 bucket name
    """
    import os
    bucket = os.environ.get('S3_BUCKET', 'fleetota-telemetry')
    logger.info(f"Using S3 bucket: {bucket}")
    return bucket


def get_recent_telemetry(bucket_name, hours=1):
    """
    Get recent telemetry files from S3 (last N hours).
    
    Args:
        bucket_name: S3 bucket name
        hours: Number of hours to look back
        
    Returns:
        list: List of S3 object keys
    """
    try:
        # Get current date/time for path
        now = datetime.now()
        prefix = f"telemetry/{now.strftime('%Y%m%d')}"
        
        logger.info(f"Scanning S3 prefix: {prefix}")
        
        # List objects in S3
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=1000  # Limit for safety
        )
        
        if 'Contents' not in response:
            logger.warning(f"No telemetry files found in {prefix}")
            return []
        
        # Get recent files (last N hours)
        cutoff_time = now - timedelta(hours=hours)
        recent_files = []
        
        for obj in response['Contents']:
            if obj['LastModified'].replace(tzinfo=None) > cutoff_time:
                recent_files.append(obj['Key'])
        
        logger.info(f"Found {len(recent_files)} recent telemetry files")
        return recent_files
        
    except Exception as e:
        logger.error(f"Error listing S3 objects: {str(e)}")
        return []


def analyze_fleet(bucket_name, telemetry_files):
    """
    Analyze fleet telemetry to determine update eligibility.
    
    Args:
        bucket_name: S3 bucket name
        telemetry_files: List of telemetry file keys
        
    Returns:
        dict: Fleet status summary
    """
    
    fleet_status = {
        'total_vehicles': 0,
        'update_eligible': 0,
        'update_in_progress': 0,
        'up_to_date': 0,
        'insufficient_battery': 0,
        'offline': 0,
        'firmware_distribution': defaultdict(int),
        'vehicles_by_status': defaultdict(list)
    }
    
    # Track unique vehicles (use dict to keep latest telemetry)
    vehicles = {}
    
    # Process each telemetry file
    for file_key in telemetry_files:
        try:
            telemetry = download_telemetry(bucket_name, file_key)
            vehicle_id = telemetry.get('vehicle_id')
            
            # Keep only latest telemetry per vehicle
            if vehicle_id not in vehicles:
                vehicles[vehicle_id] = telemetry
            else:
                # Compare timestamps and keep newer
                if telemetry.get('timestamp', '') > vehicles[vehicle_id].get('timestamp', ''):
                    vehicles[vehicle_id] = telemetry
                    
        except Exception as e:
            logger.error(f"Error processing {file_key}: {str(e)}")
            continue
    
    # Analyze each vehicle
    for vehicle_id, telemetry in vehicles.items():
        fleet_status['total_vehicles'] += 1
        
        # Extract vehicle info
        firmware_version = telemetry.get('firmware', {}).get('current_version', 'unknown')
        battery_percent = telemetry.get('battery', {}).get('percent', 0)
        status = telemetry.get('status', 'unknown')
        update_available = telemetry.get('firmware', {}).get('update_available', False)
        
        # Track firmware distribution
        fleet_status['firmware_distribution'][firmware_version] += 1
        
        # Determine update eligibility
        if status == 'updating':
            fleet_status['update_in_progress'] += 1
            fleet_status['vehicles_by_status']['updating'].append(vehicle_id)
            
        elif status == 'offline':
            fleet_status['offline'] += 1
            fleet_status['vehicles_by_status']['offline'].append(vehicle_id)
            
        elif firmware_version == LATEST_FIRMWARE_VERSION:
            fleet_status['up_to_date'] += 1
            fleet_status['vehicles_by_status']['up_to_date'].append(vehicle_id)
            
        elif battery_percent < MINIMUM_BATTERY_PERCENT:
            fleet_status['insufficient_battery'] += 1
            fleet_status['vehicles_by_status']['low_battery'].append(vehicle_id)
            
        else:
            # Vehicle is eligible for update!
            fleet_status['update_eligible'] += 1
            fleet_status['vehicles_by_status']['eligible'].append(vehicle_id)
            
            # Log high priority updates
            if firmware_version in UPDATE_PRIORITY_VERSIONS:
                logger.info(f"HIGH PRIORITY: Vehicle {vehicle_id} on critical version {firmware_version}")
    
    return fleet_status


def download_telemetry(bucket_name, object_key):
    """
    Download and parse telemetry JSON from S3.
    
    Args:
        bucket_name: S3 bucket name
        object_key: S3 object key
        
    Returns:
        dict: Parsed telemetry data
    """
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response['Body'].read().decode('utf-8')
    return json.loads(file_content)


def publish_update_metrics(fleet_status):
    """
    Publish update campaign metrics to CloudWatch.
    
    Args:
        fleet_status: Fleet status dictionary
    """
    try:
        namespace = 'FleetOTA'
        timestamp = datetime.now()
        
        metric_data = [
            # Total vehicles
            {
                'MetricName': 'TotalVehicles',
                'Value': fleet_status['total_vehicles'],
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            },
            
            # Update eligible vehicles
            {
                'MetricName': 'UpdateEligible',
                'Value': fleet_status['update_eligible'],
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            },
            
            # Updates in progress
            {
                'MetricName': 'UpdateInProgress',
                'Value': fleet_status['update_in_progress'],
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            },
            
            # Up to date vehicles
            {
                'MetricName': 'VehiclesUpToDate',
                'Value': fleet_status['up_to_date'],
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            },
            
            # Offline vehicles
            {
                'MetricName': 'VehiclesOffline',
                'Value': fleet_status['offline'],
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            },
            
            # Low battery vehicles
            {
                'MetricName': 'LowBatteryVehicles',
                'Value': fleet_status['insufficient_battery'],
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            },
            
            # Update eligibility rate (percentage)
            {
                'MetricName': 'UpdateEligibilityRate',
                'Value': (fleet_status['update_eligible'] / max(fleet_status['total_vehicles'], 1)) * 100,
                'Unit': 'Percent',
                'Timestamp': timestamp,
                'Dimensions': [{'Name': 'Fleet', 'Value': 'All'}]
            }
        ]
        
        # Add firmware version distribution metrics
        for version, count in fleet_status['firmware_distribution'].items():
            metric_data.append({
                'MetricName': 'VehiclesByFirmware',
                'Value': count,
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'Fleet', 'Value': 'All'},
                    {'Name': 'FirmwareVersion', 'Value': version}
                ]
            })
        
        # Publish to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace=namespace,
            MetricData=metric_data
        )
        
        logger.info(f"Published {len(metric_data)} update metrics to CloudWatch")
        
    except Exception as e:
        logger.error(f"Error publishing metrics: {str(e)}")
        raise


def log_summary(fleet_status):
    """
    Log fleet update summary.
    
    Args:
        fleet_status: Fleet status dictionary
    """
    logger.info("=" * 60)
    logger.info("FLEET UPDATE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Vehicles:        {fleet_status['total_vehicles']}")
    logger.info(f"Update Eligible:       {fleet_status['update_eligible']}")
    logger.info(f"Update In Progress:    {fleet_status['update_in_progress']}")
    logger.info(f"Up to Date:            {fleet_status['up_to_date']}")
    logger.info(f"Low Battery:           {fleet_status['insufficient_battery']}")
    logger.info(f"Offline:               {fleet_status['offline']}")
    logger.info(f"\nFirmware Distribution:")
    for version, count in sorted(fleet_status['firmware_distribution'].items()):
        percentage = (count / max(fleet_status['total_vehicles'], 1)) * 100
        logger.info(f"  {version}: {count} vehicles ({percentage:.1f}%)")
    logger.info("=" * 60)