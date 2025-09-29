# FleetOTA - Serverless Vehicle OTA Update Management System

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20CloudWatch-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-grade, serverless Over-The-Air (OTA) update management system designed for connected vehicle fleets. Built entirely on AWS serverless technologies to demonstrate cloud operations expertise and automotive telematics knowledge.

## 🎯 Project Overview

FleetOTA simulates a real-world automotive OTA system handling 100+ vehicles, processing telemetry data, and managing firmware update distribution—all using serverless architecture for scalability, cost-efficiency, and operational excellence.

### Key Features

- **🚗 Realistic Vehicle Simulation**: 100 simulated vehicles with authentic VINs, GPS tracking, battery monitoring, and connectivity status
- **⚡ Serverless Processing**: AWS Lambda functions for telemetry ingestion and update orchestration
- **📊 Real-Time Monitoring**: Custom CloudWatch metrics and alarms for fleet health tracking
- **📈 Interactive Dashboard**: Live visualization of fleet status, update progress, and system metrics
- **🔒 Production-Ready**: Comprehensive error handling, logging, retry logic, and security best practices
- **💰 Cost-Optimized**: Free Tier compatible architecture with efficient resource utilization

---

## 🏗️ Architecture

```
┌─────────────────┐
│  100 Vehicles   │
│   (Simulator)   │
└────────┬────────┘
         │ Telemetry Data
         ↓
┌─────────────────┐
│   Amazon S3     │
│  (Data Lake)    │
└────────┬────────┘
         │ S3 Event
         ↓
┌─────────────────┐      ┌──────────────────┐
│   Lambda        │      │   Lambda         │
│   Telemetry     │─────→│   Update         │
│   Processor     │      │   Manager        │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         └────────┬───────────────┘
                  ↓
         ┌─────────────────┐
         │  CloudWatch     │
         │  Metrics/Logs   │
         └────────┬────────┘
                  ↓
         ┌─────────────────┐
         │   Dashboard     │
         │  (Chart.js UI)  │
         └─────────────────┘
```

### Components

1. **Vehicle Simulator** (`vehicle-simulator/`)
   - Generates realistic vehicle telemetry
   - Uploads data to S3 in JSON format
   - Simulates GPS movement, battery drain, network conditions

2. **Telemetry Processor** (`lambda-functions/telemetry-processor/`)
   - Triggered by S3 events
   - Validates and enriches telemetry data
   - Publishes custom CloudWatch metrics
   - Flags vehicles requiring updates

3. **Update Manager** (`lambda-functions/update-manager/`)
   - Orchestrates OTA update campaigns
   - Manages update eligibility and scheduling
   - Tracks update success/failure rates
   - Implements retry logic for failed updates

4. **Monitoring Dashboard** (`dashboard/`)
   - Real-time fleet visualization
   - Update campaign progress tracking
   - System health metrics
   - Historical trend analysis

---

## 🚀 Quick Start

### Prerequisites

- AWS Account (Free Tier eligible)
- AWS CLI configured with appropriate credentials
- Python 3.9 or higher
- Node.js (for dashboard, optional)

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/FleetOTA-Serverless-Vehicle-Update-System.git
cd FleetOTA-Serverless-Vehicle-Update-System

# Install Python dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Set up S3 bucket (replace with unique name)
aws s3 mb s3://fleetota-telemetry-YOUR_UNIQUE_ID

# Deploy Lambda functions
cd lambda-functions/telemetry-processor
zip -r function.zip lambda_function.py
aws lambda create-function \
  --function-name FleetOTA-TelemetryProcessor \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip
```

### Running the Simulator

```bash
cd vehicle-simulator
python vehicle_generator.py --vehicles 100 --interval 60
```

---

## 📊 Monitoring & Metrics

### Custom CloudWatch Metrics

- `FleetHealth/VehiclesOnline`: Number of active vehicles
- `FleetHealth/BatteryAverage`: Average battery percentage across fleet
- `OTAUpdates/InProgress`: Active update count
- `OTAUpdates/SuccessRate`: Percentage of successful updates
- `Telemetry/DataPoints`: Telemetry messages processed per minute

### Alarms

- High telemetry processing latency (>5s)
- Low vehicle connectivity rate (<80%)
- Update failure rate exceeds threshold (>5%)
- Lambda error rate monitoring

---

## 🎓 Technical Highlights for Cloud Operations Role

### Demonstrates:

✅ **AWS Serverless Expertise**: Lambda, S3, CloudWatch, EventBridge integration  
✅ **Cost Optimization**: Free Tier usage, efficient Lambda execution, S3 lifecycle policies  
✅ **Operational Excellence**: Comprehensive logging, monitoring, and alerting  
✅ **Security Best Practices**: IAM least privilege, encrypted S3, VPC integration ready  
✅ **Scalability Design**: Handles 100+ vehicles, can scale to thousands  
✅ **Real-World Problem Solving**: Automotive OTA challenges (connectivity, rollback, scheduling)  
✅ **Production Code Quality**: Error handling, testing, documentation, CI/CD ready  

---

## 📁 Project Structure

```
├── vehicle-simulator/          # Vehicle telemetry generator
├── lambda-functions/           # AWS Lambda function code
│   ├── telemetry-processor/    # Processes incoming telemetry
│   └── update-manager/         # Manages OTA updates
├── dashboard/                  # Web-based monitoring UI
├── cloudformation/             # Infrastructure as Code templates
├── monitoring/                 # CloudWatch dashboard configs
├── docs/                       # Technical documentation
└── tests/                      # Unit and integration tests
```

---

## 🔧 Configuration

Create `vehicle-simulator/config.py`:

```python
AWS_REGION = 'us-east-1'
S3_BUCKET = 'fleetota-telemetry-YOUR_UNIQUE_ID'
VEHICLE_COUNT = 100
TELEMETRY_INTERVAL = 60  # seconds
```

---

## 📈 Roadmap

- [ ] Add DynamoDB for vehicle state persistence
- [ ] Implement SQS for update job queuing
- [ ] Add API Gateway for REST API access
- [ ] Implement Step Functions for complex update workflows
- [ ] Add SNS notifications for critical alerts
- [ ] Integrate with AWS IoT Core for real device connectivity

---

## 🤝 Contributing

This is a portfolio project, but feedback and suggestions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sarthak Zende**  
MS Computer Science Student  
Specializing in Cloud Computing & Distributed Systems

📧 Email: your.email@example.com  
🔗 LinkedIn: [linkedin.com/in/yourprofile]([https://linkedin.com/in/yourprofile](https://www.linkedin.com/in/sarthakzende/))  
💼 Portfolio: [yourportfolio.com]([https://yourportfolio.com](https://sarthakzende379.github.io/portfolio/))

---

## 🙏 Acknowledgments

- Inspired by real-world automotive OTA systems from Tesla, Rivian, and traditional OEMs
- AWS documentation and best practices references

---

**⭐ If this project helped you, please consider starring the repository!**
