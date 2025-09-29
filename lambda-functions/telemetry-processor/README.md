# Telemetry Processor Lambda Function

## Overview
Processes vehicle telemetry data uploaded to S3 and publishes metrics to CloudWatch.

## Trigger
- **Event Source**: S3 bucket
- **Event Type**: `s3:ObjectCreated:*`
- **Filter**: `telemetry/*.json`

## What It Does
1. Gets triggered when vehicle uploads telemetry JSON to S3
2. Downloads and parses the JSON file
3. Extracts key metrics (battery, GPS, connectivity, status)
4. Publishes 6 custom metrics to CloudWatch:
   - BatteryPercent
   - BatteryHealth
   - VehicleSpeed
   - SignalStrength
   - VehicleOnline
   - UpdateAvailable

## CloudWatch Metrics Published

| Metric Name | Description | Unit | Dimensions |
|-------------|-------------|------|------------|
| BatteryPercent | Battery charge level | Percent | VehicleID, VIN |
| BatteryHealth | Battery health status | Percent | VehicleID |
| VehicleSpeed | Current speed | km/h | VehicleID |
| SignalStrength | Network signal strength | dBm | VehicleID |
| VehicleOnline | Vehicle connectivity | Count (0/1) | Fleet |
| UpdateAvailable | Firmware update flag | Count (0/1) | VehicleID |

## Deployment

### Option 1: AWS Console (Easiest)

1. **Create Lambda function:**
   ```
   Function name: FleetOTA-TelemetryProcessor
   Runtime: Python 3.9
   Architecture: x86_64
   ```

2. **Copy code:**
   - Copy entire content of `lambda_function.py`
   - Paste into Lambda code editor
   - Click "Deploy"

3. **Configure permissions:**
   - Go to Configuration → Permissions
   - Add policies:
     - `AmazonS3ReadOnlyAccess`
     - `CloudWatchPutMetricData`

4. **Add S3 trigger:**
   - Click "Add trigger"
   - Select S3
   - Choose your bucket: `fleetota-telemetry-XXXXX`
   - Event type: `All object create events`
   - Prefix: `telemetry/`
   - Suffix: `.json`

### Option 2: AWS CLI

```bash
# Package Lambda function
cd lambda-functions/telemetry-processor
zip -r function.zip lambda_function.py

# Create Lambda function
aws lambda create-function \
  --function-name FleetOTA-TelemetryProcessor \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/FleetOTA-Lambda-Role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256

# Add S3 trigger permission
aws lambda add-permission \
  --function-name FleetOTA-TelemetryProcessor \
  --statement-id s3-trigger \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::YOUR_BUCKET_NAME

# Configure S3 event notification
aws s3api put-bucket-notification-configuration \
  --bucket YOUR_BUCKET_NAME \
  --notification-configuration file://s3-notification.json
```

## Testing

### Test Event (Sample)
```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "fleetota-telemetry-xxxxx"
        },
        "object": {
          "key": "telemetry/20250929/14/vehicle_1_1727616000000.json"
        }
      }
    }
  ]
}
```

### Manual Test
1. Run vehicle simulator to generate telemetry
2. Check CloudWatch Logs: `/aws/lambda/FleetOTA-TelemetryProcessor`
3. Verify metrics in CloudWatch: Namespace `FleetOTA`

## Monitoring

### View Logs
```bash
# Tail logs
aws logs tail /aws/lambda/FleetOTA-TelemetryProcessor --follow

# Get recent logs
aws logs tail /aws/lambda/FleetOTA-TelemetryProcessor --since 10m
```

### View Metrics
```bash
# List all FleetOTA metrics
aws cloudwatch list-metrics --namespace FleetOTA

# Get specific metric
aws cloudwatch get-metric-statistics \
  --namespace FleetOTA \
  --metric-name BatteryPercent \
  --start-time 2025-09-29T00:00:00Z \
  --end-time 2025-09-29T23:59:59Z \
  --period 300 \
  --statistics Average
```

## Troubleshooting

### Lambda not triggering
- Check S3 event configuration
- Verify Lambda has S3 invoke permission
- Check CloudWatch logs for errors

### Metrics not appearing
- Wait 1-2 minutes (CloudWatch delay)
- Verify Lambda is publishing successfully
- Check IAM permissions for CloudWatch

### Performance issues
- Increase Lambda memory (256MB → 512MB)
- Increase timeout (30s → 60s)
- Check for S3 throttling

## Cost Estimation (Free Tier)

| Resource | Usage | Cost |
|----------|-------|------|
| Lambda Invocations | 6,000/hour | $0.00 (Free: 1M/month) |
| Lambda Duration | ~100ms each | $0.00 (Free: 400,000 GB-s) |
| CloudWatch Metrics | 6 metrics × 100 vehicles | $0.00 (Free: 10 metrics) |
| **Total** | | **$0.00** |

## Next Steps
After this Lambda is working:
1. Create Update Manager Lambda
2. Build dashboard to visualize metrics
3. Set up CloudWatch alarms