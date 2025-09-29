"""
FleetOTA Telemetry Processor Lambda Function
============================================
Processes vehicle telemetry data uploaded to S3 and publishes metrics to CloudWatch.

Trigger: S3 Event (when new telemetry JSON file is uploaded)
Output: CloudWatch custom metrics

Author: Sarthak Zende
"""

import json
import boto3
import logging
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
cloudwatch_client = boto3.client('cloudwatch')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    Args:
        event: S3 event containing bucket and object information
        context: Lambda context object
        
    Returns:
        dict: Response with status code and message
    """
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract S3 bucket and key from event
        for record in event['Records']:
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            
            logger.info(f"Processing file: s3://{bucket_name}/{object_key}")
            
            # Download telemetry file from S3
            telemetry_data = download_telemetry(bucket_name, object_key)
            
            # Process telemetry and extract metrics
            metrics = process_telemetry(telemetry_data)
            
            # Publish metrics to CloudWatch
            publish_metrics(metrics)
            
            logger.info(f"Successfully processed telemetry for vehicle {telemetry_data.get('vehicle_id')}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Telemetry processed successfully')
        }
        
    except Exception as e:
        logger.error(f"Error processing telemetry: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }


def download_telemetry(bucket_name, object_key):
    """
    Download telemetry JSON file from S3.
    
    Args:
        bucket_name: S3 bucket name
        object_key: S3 object key (file path)
        
    Returns:
        dict: Parsed telemetry data
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')
        telemetry_data = json.loads(file_content)
        
        logger.info(f"Downloaded telemetry for vehicle {telemetry_data.get('vehicle_id')}")
        return telemetry_data
        
    except Exception as e:
        logger.error(f"Error downloading from S3: {str(e)}")
        raise


def process_telemetry(telemetry_data):
    """
    Extract key metrics from telemetry data.
    
    Args:
        telemetry_data: Raw telemetry dictionary
        
    Returns:
        dict: Processed metrics
    """
    try:
        metrics = {
            'vehicle_id': telemetry_data.get('vehicle_id'),
            'vin': telemetry_data.get('vin'),
            'timestamp': telemetry_data.get('timestamp'),
            
            # Battery metrics
            'battery_percent': telemetry_data.get('battery', {}).get('percent', 0),
            'battery_health': telemetry_data.get('battery', {}).get('health', 0),
            
            # GPS metrics
            'speed_kmh': telemetry_data.get('gps', {}).get('speed_kmh', 0),
            'latitude': telemetry_data.get('gps', {}).get('latitude'),
            'longitude': telemetry_data.get('gps', {}).get('longitude'),
            
            # Connectivity metrics
            'signal_strength': telemetry_data.get('connectivity', {}).get('signal_strength_dbm', 0),
            'connected': telemetry_data.get('connectivity', {}).get('connected', False),
            
            # Status
            'status': telemetry_data.get('status', 'unknown'),
            'firmware_version': telemetry_data.get('firmware', {}).get('current_version', 'unknown'),
            'update_available': telemetry_data.get('firmware', {}).get('update_available', False)
        }
        
        logger.info(f"Processed metrics for vehicle {metrics['vehicle_id']}: "
                   f"Battery={metrics['battery_percent']}%, Speed={metrics['speed_kmh']} km/h")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error processing telemetry: {str(e)}")
        raise


def publish_metrics(metrics):
    """
    Publish metrics to CloudWatch.
    
    Args:
        metrics: Dictionary of processed metrics
    """
    try:
        namespace = 'FleetOTA'
        timestamp = datetime.now()
        
        # Prepare metric data
        metric_data = [
            # Battery metrics
            {
                'MetricName': 'BatteryPercent',
                'Value': metrics['battery_percent'],
                'Unit': 'Percent',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'VehicleID', 'Value': str(metrics['vehicle_id'])},
                    {'Name': 'VIN', 'Value': metrics['vin']}
                ]
            },
            {
                'MetricName': 'BatteryHealth',
                'Value': metrics['battery_health'],
                'Unit': 'Percent',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'VehicleID', 'Value': str(metrics['vehicle_id'])}
                ]
            },
            
            # Speed metric
            {
                'MetricName': 'VehicleSpeed',
                'Value': metrics['speed_kmh'],
                'Unit': 'None',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'VehicleID', 'Value': str(metrics['vehicle_id'])}
                ]
            },
            
            # Connectivity metric
            {
                'MetricName': 'SignalStrength',
                'Value': abs(metrics['signal_strength']),  # Make positive for better visualization
                'Unit': 'None',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'VehicleID', 'Value': str(metrics['vehicle_id'])}
                ]
            },
            
            # Vehicle online status (1 = online, 0 = offline)
            {
                'MetricName': 'VehicleOnline',
                'Value': 1 if metrics['status'] == 'online' else 0,
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'Fleet', 'Value': 'All'}
                ]
            },
            
            # Update available flag
            {
                'MetricName': 'UpdateAvailable',
                'Value': 1 if metrics['update_available'] else 0,
                'Unit': 'Count',
                'Timestamp': timestamp,
                'Dimensions': [
                    {'Name': 'VehicleID', 'Value': str(metrics['vehicle_id'])}
                ]
            }
        ]
        
        # Publish to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace=namespace,
            MetricData=metric_data
        )
        
        logger.info(f"Published {len(metric_data)} metrics to CloudWatch namespace '{namespace}'")
        
    except Exception as e:
        logger.error(f"Error publishing metrics to CloudWatch: {str(e)}")
        raise


def get_fleet_summary():
    """
    Optional: Get aggregated fleet statistics.
    This could be called by another service or API.
    """
    # This is a placeholder for future enhancement
    # Could query DynamoDB or aggregate CloudWatch metrics
    pass