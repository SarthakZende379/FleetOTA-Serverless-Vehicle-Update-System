# FleetOTA Quick Start Guide

Get your vehicle simulator running in **15 minutes**!

## 🚀 Prerequisites (5 minutes)

```bash
# 1. Verify Python 3.9+
python3 --version

# 2. Verify AWS CLI
aws --version

# 3. Configure AWS (if not done)
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json

# 4. Test AWS connection
aws sts get-caller-identity
```

---

## 📦 Setup (5 minutes)

### Step 1: Create S3 Bucket

```bash
# Create unique bucket name
BUCKET_NAME="fleetota-telemetry-$(whoami)-$(date +%s)"
echo "Your bucket: $BUCKET_NAME"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Verify
aws s3 ls | grep fleetota
```

### Step 2: Setup Project

```bash
# Create project directory
mkdir -p FleetOTA/vehicle-simulator
cd FleetOTA/vehicle-simulator

# Install boto3
pip3 install boto3

# Download vehicle_generator.py and config.py
# (Copy the code from the artifacts above)
```

### Step 3: Update Configuration

Edit `config.py` and change:
```python
S3_BUCKET = 'YOUR_BUCKET_NAME_HERE'  # Replace with $BUCKET_NAME
```

---

## 🏃 Run Simulator (5 minutes)

### Quick Test (5 vehicles, 2 minutes)

```bash
python3 vehicle_generator.py \
  --vehicles 5 \
  --duration 2 \
  --interval 30 \
  --bucket YOUR_BUCKET_NAME
```

**Expected Output:**
```
======================================================================
FleetOTA Vehicle Telemetry Generator
======================================================================
Vehicles:    5
Duration:    2 minutes
Interval:    30 seconds
S3 Bucket:   fleetota-telemetry-xxxxx
AWS Region:  us-east-1
======================================================================

2025-09-29 10:30:00 - INFO - Connected to S3 bucket: fleetota-telemetry-xxxxx
2025-09-29 10:30:01 - INFO - Vehicle 1 initialized: VIN=5YJSA1E14MF123456
2025-09-29 10:30:01 - INFO - Vehicle 2 initialized: VIN=1FAHP3F23CL234567
...
2025-09-29 10:30:05 - INFO - Iteration 1: Generating telemetry for 5 vehicles
2025-09-29 10:30:10 - INFO - Iteration 1 complete: 5 successful, 0 failed
```

### Verify Data in S3

```bash
# List uploaded files
aws s3 ls s3://$BUCKET_NAME/telemetry/ --recursive | head -10

# Download and view a sample
aws s3 cp s3://$BUCKET_NAME/telemetry/ . --recursive --exclude "*" --include "vehicle_1_*.json" | head -1
cat vehicle_1_*.json | python3 -m json.tool
```

### Full Production Run (100 vehicles, 1 hour)

```bash
python3 vehicle_generator.py \
  --vehicles 100 \
  --duration 60 \
  --interval 60 \
  --bucket YOUR_BUCKET_NAME \
  --log-level INFO
```

---

## 📊 Monitor Progress

### In Another Terminal

```bash
# Watch log file
tail -f vehicle_simulator.log

# Count files in S3
watch -n 10 'aws s3 ls s3://$BUCKET_NAME/telemetry/ --recursive | wc -l'

# Check S3 bucket size
aws s3 ls s3://$BUCKET_NAME --recursive --summarize | grep "Total Size"
```

---

## ✅ Success Criteria

After the 2-minute test, you should see:

- ✅ 5 vehicles initialized with unique VINs
- ✅ ~10 telemetry files in S3 (5 vehicles × 2 iterations)
- ✅ No errors in logs
- ✅ Summary statistics showing 100% success rate

---

## 🎉 What's Next?

Now that your simulator is working:

1. **Create Lambda Functions** (Next 2 hours)
   - Telemetry Processor
   - Update Manager

2. **Setup CloudWatch** (Next 1 hour)
   - Custom metrics
   - Alarms and dashboards

3. **Build Dashboard** (Next 1.5 hours)
   - Real-time visualization
   - Chart.js integration

4. **Polish & Document** (Final 1.5 hours)
   - README with screenshots
   - Architecture diagram
   - GitHub repository polish

---

## 🐛 Common Issues

### Issue: "NoCredentialsError"
```bash
# Solution: Configure AWS
aws configure
```

### Issue: "Bucket does not exist"
```bash
# Solution: Verify bucket name
aws s3 ls | grep fleetota

# Or create it
aws s3 mb s3://YOUR_BUCKET_NAME
```

### Issue: "Access Denied"
```bash
# Solution: Check IAM permissions
aws iam get-user

# Ensure your user has S3 access
aws s3api put-bucket-policy --bucket YOUR_BUCKET_NAME --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
  }]
}'
```

---

## 💡 Pro Tips

1. **Start Small**: Test with 5 vehicles first
2. **Monitor Costs**: Free Tier covers ~100 vehicles for 1 hour
3. **Save Bucket Name**: `echo $BUCKET_NAME >> ~/.bashrc`
4. **Background Run**: `nohup python3 vehicle_generator.py ... &`
5. **Stop Anytime**: `Ctrl+C` to gracefully stop

---

## 📈 Expected AWS Costs (Free Tier)

| Service | Usage | Cost |
|---------|-------|------|
| S3 PUT Requests | ~6,000 | $0.00 (Free Tier: 2,000/month) |
| S3 Storage | ~50 MB | $0.00 (Free Tier: 5 GB) |
| Data Transfer | ~50 MB | $0.00 (Free Tier: 1 GB) |
| **Total** | | **$0.00** |

**Note**: Running 100 vehicles for 1 hour = ~6,000 S3 uploads = FREE!

---

## 🎯 Ready for KPIT Interview?

You can now demonstrate:

✅ AWS S3 expertise  
✅ Python boto3 proficiency  
✅ Production-quality code  
✅ Error handling and logging  
✅ Realistic automotive telemetry  
✅ Scalable architecture design  

**Next**: Build Lambda functions to process this data!

---

**Questions? Issues? Check SETUP.md for detailed troubleshooting!**