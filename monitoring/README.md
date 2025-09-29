# CloudWatch Monitoring Configuration

## Overview
Pre-configured CloudWatch dashboards and alarms for FleetOTA system monitoring.

## Files

### 1. `cloudwatch-dashboard.json`
Complete dashboard configuration with 7 widgets:
- Fleet online status (time series)
- Battery levels (time series)
- Update campaign status (stacked)
- Signal strength (time series)
- Vehicle speed (time series)
- Firmware distribution (single value)
- Recent errors (log insights)

### 2. `alarms.json`
5 pre-configured alarms:
- High offline vehicles (>30%)
- Low fleet battery (<40%)
- High update failure rate
- Lambda function errors
- No telemetry data received

## Setup CloudWatch Dashboard

### Option 1: AWS Console

1. Go to **CloudWatch** → **Dashboards**
2. Click **Create dashboard**
3. Name it: `FleetOTA-Dashboard`
4. Click **Actions** → **View/edit source**
5. Copy entire content from `cloudwatch-dashboard.json`
6. Paste and click **Update**

### Option 2: AWS CLI

```bash
cd monitoring

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name FleetOTA-Dashboard \
  --dashboard-body file://cloudwatch-dashboard.json

# Verify
aws cloudwatch list-dashboards
```

## Setup CloudWatch Alarms

### Create Alarms via CLI

```bash
# High Offline Vehicles Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name FleetOTA-HighOfflineVehicles \
  --alarm-description "Alert when more than 30% of fleet is offline" \
  --metric-name VehiclesOffline \
  --namespace FleetOTA \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 30 \
  --comparison-operator GreaterThanThreshold

# Low Fleet Battery Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name FleetOTA-LowFleetBattery \
  --alarm-description "Alert when average fleet battery drops below 40%" \
  --metric-name BatteryPercent \
  --namespace FleetOTA \
  --statistic Average \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 40 \
  --comparison-operator LessThanThreshold

# Lambda Errors Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name FleetOTA-LambdaErrors \
  --alarm-description "Alert on Lambda function errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=FleetOTA-TelemetryProcessor \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold

# No Telemetry Data Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name FleetOTA-NoTelemetryData \
  --alarm-description "Alert when no telemetry data received for 10 minutes" \
  --metric-name VehicleOnline \
  --namespace FleetOTA \
  --statistic SampleCount \
  --period 600 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --treat-missing-data breaching
```

### Add SNS Notifications (Optional)

```bash
# Create SNS topic
aws sns create-topic --name FleetOTA-Alerts

# Subscribe your email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:FleetOTA-Alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Add SNS to alarms
aws cloudwatch put-metric-alarm \
  --alarm-name FleetOTA-HighOfflineVehicles \
  --alarm-actions arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:FleetOTA-Alerts \
  ... (other parameters)
```

## Viewing Metrics

### List All FleetOTA Metrics

```bash
aws cloudwatch list-metrics --namespace FleetOTA
```

### Get Specific Metric Data

```bash
# Get vehicle online count for last hour
aws cloudwatch get-metric-statistics \
  --namespace FleetOTA \
  --metric-name VehicleOnline \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Get average battery level
aws cloudwatch get-metric-statistics \
  --namespace FleetOTA \
  --metric-name BatteryPercent \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Minimum,Maximum
```

## Monitoring Best Practices

### 1. Set Up Alarms
- Always have alarms for critical metrics
- Use SNS for email/SMS notifications
- Test alarms after creation

### 2. Regular Dashboard Reviews
- Check dashboard daily during testing
- Monitor trends over time
- Adjust thresholds as needed

### 3. Log Analysis
- Use CloudWatch Logs Insights
- Set up log retention policies
- Export logs for long-term storage

### 4. Cost Optimization
- Use appropriate metric periods (300s default)
- Set log retention to 7 days for testing
- Delete unused metrics

## Sample Queries (CloudWatch Logs Insights)

### Find All Errors

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

### Count Telemetry by Vehicle

```
fields @timestamp, vehicle_id
| filter @message like /vehicle_id/
| stats count() by vehicle_id
| sort count desc
```

### Average Processing Time

```
fields @duration
| filter @type = "REPORT"
| stats avg(@duration), max(@duration), min(@duration)
```

### Failed Lambda Invocations

```
fields @timestamp, @message
| filter @type = "REPORT" and @message like /Error/
| sort @timestamp desc
```

## Troubleshooting

### Metrics Not Appearing

**Check Lambda Execution:**
```bash
aws logs tail /aws/lambda/FleetOTA-TelemetryProcessor --since 10m
```

**Verify IAM Permissions:**
- Ensure Lambda has `cloudwatch:PutMetricData` permission

**Check Namespace:**
- All metrics should be in `FleetOTA` namespace
- Case-sensitive!

### Dashboard Not Loading

- Verify region is correct (us-east-1)
- Check metric names match exactly
- Ensure data exists for time range

### Alarms Not Triggering

- Check alarm state: `aws cloudwatch describe-alarms`
- Verify threshold values are appropriate
- Ensure metrics are being published
- Check evaluation periods

## Cost Estimation

| Resource | Usage | Cost |
|----------|-------|------|
| Custom Metrics | 10 metrics | $0.30/month |
| Dashboard | 1 dashboard | Free (3 free) |
| Alarms | 5 alarms | Free (10 free) |
| Log Storage | 1 GB/month | $0.50/month |
| **Total** | | **~$0.80/month** |

## Next Steps

1. ✅ Create CloudWatch dashboard
2. ✅ Set up critical alarms
3. ⏭️ Add SNS notifications
4. ⏭️ Test alarm triggers
5. ⏭️ Review metrics weekly

## Interview Talking Points

**For KPIT:**
- Comprehensive monitoring strategy
- Proactive alerting system
- Cost-optimized CloudWatch usage
- Production-ready observability
- Real-time fleet health tracking