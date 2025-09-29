# Update Manager Lambda Function

## Overview
Manages OTA firmware updates for the vehicle fleet by analyzing telemetry and determining update eligibility.

## Trigger
- **Event Source**: CloudWatch EventBridge (Scheduled)
- **Schedule**: Every 5 minutes (cron: `rate(5 minutes)`)
- **Alternative**: Manual trigger via AWS Console or API Gateway

## What It Does
1. Scans recent telemetry data from S3
2. Identifies unique vehicles and their latest status
3. Determines update eligibility based on:
   - Current firmware version
   - Battery level (must be > 50%)
   - Vehicle status (must be online)
4. Publishes update campaign metrics to CloudWatch
5. Logs summary statistics

## Update Eligibility Rules

A vehicle is eligible for update if:
- ✅ Status is "online" (not offline or already updating)
- ✅ Battery > 50%
- ✅ Firmware version is not latest (currently 2.0.0)

Priority updates for vehicles on versions: 1.2.0, 1.2.1 (critical old versions)

## CloudWatch Metrics Published

| Metric Name | Description | Unit |
|-------------|-------------|------|
| TotalVehicles | Total vehicles in fleet | Count |
| UpdateEligible | Vehicles eligible for update | Count |
| UpdateInProgress | Vehicles currently updating | Count |
| VehiclesUpToDate | Vehicles on latest firmware | Count |
| VehiclesOffline | Offline vehicles | Count |
| LowBatteryVehicles | Vehicles with battery < 50% | Count |
| UpdateEligibilityRate | Percentage of eligible vehicles | Percent |
| VehiclesByFirmware | Count by firmware version | Count |

## Deployment

### Option 1: AWS Console

1. **Create Lambda function:**
   ```
   Function name: FleetOTA-UpdateManager
   Runtime: Python 3.9
   Architecture: x86_64
   Memory: 256 MB
   Timeout: 60 seconds
   ```

2. **Copy code:**
   - Paste `lambda_function.py` content
   - Click "Deploy"

3. **Set environment variable:**
   - Key: `S3_BUCKET`
   - Value: `fleetota-telemetry-XXXXX`

4. **Configure permissions:**
   - Add policies:
     - `AmazonS3ReadOnlyAccess`
     - `CloudWatchPutMetricData`

5. **Add EventBridge trigger:**
   - Create new rule: `FleetOTA-UpdateSchedule`
   - Schedule: `rate(5 minutes)`
   - Target: This Lambda function

### Option 2: AWS CLI

```bash
cd lambda-functions/update-manager

# Package function
zip function.zip lambda_function.py

# Create function
aws lambda create-function \
  --function-name FleetOTA-UpdateManager \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/FleetOTA-Lambda-Role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 60 \
  --memory-size 256 \
  --environment Variables="{S3_BUCKET=YOUR_BUCKET_NAME}"

# Create EventBridge rule
aws events put-rule \
  --name FleetOTA-UpdateSchedule \
  --schedule-expression "rate(5 minutes)"

# Add Lambda permission for EventBridge
aws lambda add-permission \
  --function-name FleetOTA-UpdateManager \
  --statement-id eventbridge-trigger \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/FleetOTA-UpdateSchedule

# Connect rule to Lambda
aws events put-targets \
  --rule FleetOTA-UpdateSchedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:FleetOTA-UpdateManager"
```

## Testing

### Manual Test
```bash
# Invoke Lambda manually
aws lambda invoke \
  --function-name FleetOTA-UpdateManager \
  --payload '{}' \
  response.json

# View response
cat response.json
```

### Test Event (Console)
```json
{
  "source": "aws.events",
  "detail-type": "Scheduled Event",
  "time": "2025-09-29T14:00:00Z"
}
```

## Monitoring

### View Logs
```bash
# Tail logs
aws logs tail /aws/lambda/FleetOTA-UpdateManager --follow

# Get summary logs
aws logs tail /aws/lambda/FleetOTA-UpdateManager --since 1h | grep "FLEET UPDATE SUMMARY" -A 20
```

### View Metrics
```bash
# List update metrics
aws cloudwatch list-metrics --namespace FleetOTA --metric-name UpdateEligible

# Get update eligibility over time
aws cloudwatch get-metric-statistics \
  --namespace FleetOTA \
  --metric-name UpdateEligible \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## How It Works (Simple Explanation)

```
Every 5 minutes:
1. Lambda wakes up (EventBridge trigger)
2. Scans S3 for recent telemetry files
3. Reads latest status for each vehicle
4. Checks: "Can this vehicle update?"
   - Online? ✓
   - Battery > 50%? ✓
   - Old firmware? ✓
5. Counts eligible vehicles
6. Sends metrics to CloudWatch
7. Logs summary and sleeps until next run
```

## Example Output

```
============================================================
FLEET UPDATE SUMMARY
============================================================
Total Vehicles:        100
Update Eligible:       35
Update In Progress:    5
Up to Date:            20
Low Battery:           15
Offline:               25

Firmware Distribution:
  1.2.0: 10 vehicles (10.0%)
  1.2.1: 15 vehicles (15.0%)
  1.3.0: 25 vehicles (25.0%)
  1.3.1: 30 vehicles (30.0%)
  1.4.0: 15 vehicles (15.0%)
  2.0.0: 5 vehicles (5.0%)
============================================================
```

## Troubleshooting

### No vehicles found
- Check vehicle simulator is running
- Verify S3 bucket name in environment variable
- Ensure telemetry files are < 1 hour old

### Metrics not appearing
- Wait 1-2 minutes for CloudWatch sync
- Check Lambda execution logs for errors
- Verify IAM permissions

### Lambda timeout
- Increase timeout to 120 seconds
- Reduce MaxKeys in S3 list operation
- Add pagination for large fleets

## Cost Estimation

| Resource | Usage | Cost |
|----------|-------|------|
| Lambda Invocations | 12/hour (every 5 min) | $0.00 |
| Lambda Duration | ~5s each | $0.00 |
| S3 List Operations | 12/hour | $0.00 |
| CloudWatch Metrics | 8 metrics | $0.00 |
| **Total** | | **$0.00** |

## Future Enhancements
- DynamoDB table for vehicle state tracking
- SNS notifications for critical updates
- Step Functions for multi-stage updates
- Automatic rollback on failure
- A/B testing for firmware versions