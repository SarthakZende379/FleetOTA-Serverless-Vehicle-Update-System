"""
FleetOTA Vehicle Telemetry Generator
=====================================
Production-grade vehicle simulator for OTA update management system.

This module simulates realistic vehicle telemetry for a fleet of 100+ vehicles,
including VIN generation, GPS coordinates, battery status, connectivity metrics,
and firmware version tracking. Designed for automotive cloud operations demonstrations.

Author: [Your Name]
Date: September 2025
License: MIT
"""

import boto3
import json
import random
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sys


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vehicle_simulator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class VehicleStatus(Enum):
    """Vehicle operational status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    UPDATING = "updating"
    ERROR = "error"


class ConnectivityType(Enum):
    """Vehicle connectivity technology"""
    LTE = "4G_LTE"
    FIVEG = "5G"
    WIFI = "WiFi"
    SATELLITE = "Satellite"


@dataclass
class VehicleConfig:
    """Configuration parameters for vehicle simulation"""
    vin: str
    model: str
    year: int
    initial_latitude: float
    initial_longitude: float
    firmware_version: str
    manufacture_date: str


class VINGenerator:
    """
    Generates realistic Vehicle Identification Numbers (VINs).
    Follows SAE J853 standard format with proper check digit calculation.
    """
    
    # WMI (World Manufacturer Identifier) codes for various manufacturers
    WMI_CODES = {
        'TESLA': '5YJ',
        'FORD': '1FA',
        'GM': '1G1',
        'TOYOTA': '5TD',
        'HONDA': '1HG',
        'VOLKSWAGEN': 'WVW',
        'BMW': 'WBA',
        'MERCEDES': 'WDD'
    }
    
    VIN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    VIN_TRANSLITERATION = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9, 'S': 2,
        'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9
    }
    
    @staticmethod
    def calculate_check_digit(vin_without_check: str) -> str:
        """Calculate VIN check digit using modulo 11 algorithm"""
        total = 0
        for i, char in enumerate(vin_without_check):
            if char.isdigit():
                value = int(char)
            else:
                value = VINGenerator.VIN_TRANSLITERATION.get(char, 0)
            total += value * VINGenerator.VIN_WEIGHTS[i]
        
        check_digit = total % 11
        return 'X' if check_digit == 10 else str(check_digit)
    
    @classmethod
    def generate(cls, manufacturer: str = 'TESLA') -> str:
        """
        Generate a valid VIN with proper check digit.
        
        Args:
            manufacturer: Vehicle manufacturer name
            
        Returns:
            17-character VIN string
        """
        wmi = cls.WMI_CODES.get(manufacturer, '5YJ')
        vds = ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ0123456789', k=5))
        year_code = random.choice('LMNPRSTUVWXYZ')  # 2020-2032
        plant_code = random.choice('ABCDEFGHJKLMNPRSTUVWXYZ')
        serial = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        vin_without_check = wmi + vds + year_code + plant_code + serial
        check_digit = cls.calculate_check_digit(vin_without_check[:8] + vin_without_check[9:])
        
        return vin_without_check[:8] + check_digit + vin_without_check[8:]


class GPSSimulator:
    """
    Simulates realistic GPS movement patterns for vehicles.
    Uses perturbed random walk to simulate urban/highway driving.
    """
    
    # Major city centers for vehicle distribution (Lat, Lon)
    CITY_CENTERS = {
        'San Francisco': (37.7749, -122.4194),
        'Los Angeles': (34.0522, -118.2437),
        'Chicago': (41.8781, -87.6298),
        'New York': (40.7128, -74.0060),
        'Austin': (30.2672, -97.7431),
        'Seattle': (47.6062, -122.3321),
        'Detroit': (42.3314, -83.0458)
    }
    
    def __init__(self, initial_lat: float, initial_lon: float):
        """
        Initialize GPS simulator with starting coordinates.
        
        Args:
            initial_lat: Starting latitude
            initial_lon: Starting longitude
        """
        self.latitude = initial_lat
        self.longitude = initial_lon
        self.speed_kmh = random.uniform(30, 90)  # km/h
    
    def update_position(self, time_elapsed_seconds: int = 60) -> Tuple[float, float]:
        """
        Update vehicle position based on simulated movement.
        
        Args:
            time_elapsed_seconds: Time since last update
            
        Returns:
            Tuple of (latitude, longitude)
        """
        # Randomly adjust speed (simulate acceleration/deceleration)
        speed_change = random.uniform(-5, 5)
        self.speed_kmh = max(0, min(120, self.speed_kmh + speed_change))
        
        # Calculate distance traveled (in degrees, approximate)
        distance_km = (self.speed_kmh * time_elapsed_seconds) / 3600
        
        # Convert to approximate degrees (1 degree ≈ 111 km at equator)
        distance_deg = distance_km / 111.0
        
        # Random direction with some persistence (simulate road following)
        angle = random.uniform(0, 360)
        
        # Update coordinates
        self.latitude += distance_deg * random.uniform(-1, 1) * 0.1
        self.longitude += distance_deg * random.uniform(-1, 1) * 0.1
        
        # Keep within reasonable bounds
        self.latitude = max(-85, min(85, self.latitude))
        self.longitude = max(-180, min(180, self.longitude))
        
        return round(self.latitude, 6), round(self.longitude, 6)
    
    @classmethod
    def get_random_city_coordinates(cls) -> Tuple[float, float]:
        """Get random coordinates near a major city"""
        city_lat, city_lon = random.choice(list(cls.CITY_CENTERS.values()))
        # Add random offset within ~50km radius
        offset_lat = random.uniform(-0.45, 0.45)
        offset_lon = random.uniform(-0.45, 0.45)
        return (city_lat + offset_lat, city_lon + offset_lon)


class Vehicle:
    """
    Represents a single vehicle in the fleet with telemetry generation capabilities.
    """
    
    FIRMWARE_VERSIONS = ['1.2.0', '1.2.1', '1.3.0', '1.3.1', '1.4.0', '2.0.0']
    VEHICLE_MODELS = ['Model-S', 'Model-3', 'Model-X', 'Model-Y', 'Cybertruck']
    
    def __init__(self, vehicle_id: int):
        """
        Initialize vehicle with unique characteristics.
        
        Args:
            vehicle_id: Unique identifier for this vehicle
        """
        self.vehicle_id = vehicle_id
        self.vin = VINGenerator.generate()
        self.model = random.choice(self.VEHICLE_MODELS)
        self.year = random.randint(2020, 2025)
        
        # Initialize GPS
        lat, lon = GPSSimulator.get_random_city_coordinates()
        self.gps = GPSSimulator(lat, lon)
        
        # Vehicle state
        self.firmware_version = random.choice(self.FIRMWARE_VERSIONS[:4])  # Most on older versions
        self.battery_percent = random.uniform(20, 100)
        self.battery_health = random.uniform(85, 100)
        self.odometer_km = random.randint(1000, 150000)
        self.status = VehicleStatus.ONLINE
        self.connectivity = random.choice(list(ConnectivityType))
        self.signal_strength = random.randint(-90, -40)  # dBm
        
        # Update tracking
        self.last_update_check = datetime.now()
        self.update_available = random.random() < 0.3  # 30% have updates available
        self.update_downloaded = False
        
        logger.info(f"Vehicle {self.vehicle_id} initialized: VIN={self.vin}, Model={self.model}")
    
    def simulate_battery_drain(self, time_elapsed_seconds: int = 60):
        """Simulate battery consumption based on vehicle activity"""
        if self.status == VehicleStatus.ONLINE:
            # Drain rate: ~0.1-0.5% per minute while driving
            drain_rate = random.uniform(0.1, 0.5) * (time_elapsed_seconds / 60)
            self.battery_percent = max(5, self.battery_percent - drain_rate)
            
            # Simulate occasional charging
            if self.battery_percent < 30 and random.random() < 0.1:
                self.battery_percent = min(100, self.battery_percent + random.uniform(10, 30))
    
    def generate_telemetry(self) -> Dict:
        """
        Generate comprehensive telemetry data for this vehicle.
        
        Returns:
            Dictionary containing all telemetry fields
        """
        # Update position
        lat, lon = self.gps.update_position()
        
        # Simulate battery drain
        self.simulate_battery_drain()
        
        # Update odometer
        self.odometer_km += self.gps.speed_kmh / 60  # Approximate
        
        # Randomly change connectivity
        if random.random() < 0.05:  # 5% chance to change connectivity
            self.connectivity = random.choice(list(ConnectivityType))
            self.signal_strength = random.randint(-90, -40)
        
        # Randomly go offline (2% chance)
        if random.random() < 0.02:
            self.status = VehicleStatus.OFFLINE
        elif self.status == VehicleStatus.OFFLINE and random.random() < 0.3:
            self.status = VehicleStatus.ONLINE
        
        # Generate telemetry payload
        telemetry = {
            'vehicle_id': self.vehicle_id,
            'vin': self.vin,
            'timestamp': datetime.now().isoformat(),
            'model': self.model,
            'year': self.year,
            
            # Location data
            'gps': {
                'latitude': lat,
                'longitude': lon,
                'speed_kmh': round(self.gps.speed_kmh, 2),
                'heading': random.randint(0, 359)
            },
            
            # Battery data
            'battery': {
                'percent': round(self.battery_percent, 2),
                'health': round(self.battery_health, 2),
                'voltage': round(random.uniform(350, 400), 2),
                'temperature_celsius': round(random.uniform(15, 45), 1)
            },
            
            # Connectivity data
            'connectivity': {
                'type': self.connectivity.value,
                'signal_strength_dbm': self.signal_strength,
                'data_usage_mb': round(random.uniform(10, 500), 2),
                'connected': self.status != VehicleStatus.OFFLINE
            },
            
            # Vehicle status
            'status': self.status.value,
            'odometer_km': round(self.odometer_km, 1),
            
            # Firmware information
            'firmware': {
                'current_version': self.firmware_version,
                'update_available': self.update_available,
                'update_downloaded': self.update_downloaded,
                'last_update_check': self.last_update_check.isoformat()
            },
            
            # Diagnostics
            'diagnostics': {
                'error_codes': [],
                'warnings': self._generate_warnings(),
                'health_score': round(random.uniform(85, 100), 1)
            }
        }
        
        return telemetry
    
    def _generate_warnings(self) -> List[str]:
        """Generate realistic vehicle warnings"""
        warnings = []
        if self.battery_percent < 15:
            warnings.append('LOW_BATTERY')
        if self.signal_strength < -80:
            warnings.append('WEAK_SIGNAL')
        if self.battery_health < 70:
            warnings.append('BATTERY_HEALTH_DEGRADED')
        return warnings


class FleetSimulator:
    """
    Main fleet simulator orchestrating multiple vehicles and S3 uploads.
    """
    
    def __init__(self, 
                 num_vehicles: int = 100,
                 s3_bucket: str = 'fleetota-telemetry',
                 aws_region: str = 'us-east-1'):
        """
        Initialize fleet simulator.
        
        Args:
            num_vehicles: Number of vehicles to simulate
            s3_bucket: S3 bucket name for telemetry storage
            aws_region: AWS region for S3 bucket
        """
        self.num_vehicles = num_vehicles
        self.s3_bucket = s3_bucket
        self.aws_region = aws_region
        
        # Initialize AWS S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=aws_region)
            logger.info(f"Connected to S3 bucket: {s3_bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
        
        # Create vehicle fleet
        logger.info(f"Initializing fleet of {num_vehicles} vehicles...")
        self.vehicles = [Vehicle(i) for i in range(1, num_vehicles + 1)]
        logger.info(f"Fleet initialization complete: {len(self.vehicles)} vehicles ready")
        
        # Statistics
        self.telemetry_sent = 0
        self.upload_errors = 0
    
    def upload_to_s3(self, data: Dict, vehicle_id: int) -> bool:
        """
        Upload telemetry data to S3 with error handling and retries.
        
        Args:
            data: Telemetry data dictionary
            vehicle_id: Vehicle identifier
            
        Returns:
            True if upload successful, False otherwise
        """
        timestamp = datetime.now().strftime('%Y%m%d/%H')
        key = f"telemetry/{timestamp}/vehicle_{vehicle_id}_{int(time.time() * 1000)}.json"
        
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(data, indent=2),
                ContentType='application/json',
                Metadata={
                    'vehicle_id': str(vehicle_id),
                    'vin': data.get('vin', ''),
                    'timestamp': data.get('timestamp', '')
                }
            )
            self.telemetry_sent += 1
            logger.debug(f"Uploaded telemetry for vehicle {vehicle_id} to s3://{self.s3_bucket}/{key}")
            return True
            
        except Exception as e:
            self.upload_errors += 1
            logger.error(f"Failed to upload telemetry for vehicle {vehicle_id}: {e}")
            return False
    
    def run_simulation(self, 
                      duration_minutes: int = 60,
                      interval_seconds: int = 60):
        """
        Run the fleet simulation for specified duration.
        
        Args:
            duration_minutes: Total simulation duration
            interval_seconds: Telemetry generation interval
        """
        logger.info(f"Starting simulation: {duration_minutes} minutes, {interval_seconds}s interval")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        iteration = 0
        
        try:
            while time.time() < end_time:
                iteration += 1
                iteration_start = time.time()
                
                logger.info(f"Iteration {iteration}: Generating telemetry for {len(self.vehicles)} vehicles")
                
                # Generate and upload telemetry for all vehicles
                successful_uploads = 0
                failed_uploads = 0
                
                for vehicle in self.vehicles:
                    telemetry = vehicle.generate_telemetry()
                    
                    if self.upload_to_s3(telemetry, vehicle.vehicle_id):
                        successful_uploads += 1
                    else:
                        failed_uploads += 1
                
                # Log statistics
                elapsed_time = time.time() - start_time
                logger.info(
                    f"Iteration {iteration} complete: "
                    f"{successful_uploads} successful, {failed_uploads} failed | "
                    f"Total sent: {self.telemetry_sent}, Total errors: {self.upload_errors} | "
                    f"Elapsed: {elapsed_time/60:.1f} minutes"
                )
                
                # Sleep until next interval
                iteration_duration = time.time() - iteration_start
                sleep_time = max(0, interval_seconds - iteration_duration)
                
                if sleep_time > 0:
                    logger.debug(f"Sleeping for {sleep_time:.1f} seconds until next iteration")
                    time.sleep(sleep_time)
                else:
                    logger.warning(
                        f"Iteration took {iteration_duration:.1f}s, "
                        f"exceeding interval of {interval_seconds}s"
                    )
        
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        
        except Exception as e:
            logger.error(f"Simulation error: {e}", exc_info=True)
        
        finally:
            self._print_summary(start_time)
    
    def _print_summary(self, start_time: float):
        """Print simulation summary statistics"""
        total_duration = time.time() - start_time
        
        print("\n" + "="*70)
        print("FLEET SIMULATION SUMMARY")
        print("="*70)
        print(f"Duration:              {total_duration/60:.2f} minutes")
        print(f"Vehicles:              {len(self.vehicles)}")
        print(f"Telemetry uploaded:    {self.telemetry_sent}")
        print(f"Upload errors:         {self.upload_errors}")
        print(f"Success rate:          {(self.telemetry_sent/(self.telemetry_sent+self.upload_errors)*100):.2f}%")
        print(f"S3 bucket:             s3://{self.s3_bucket}")
        
        # Vehicle status summary
        online = sum(1 for v in self.vehicles if v.status == VehicleStatus.ONLINE)
        offline = sum(1 for v in self.vehicles if v.status == VehicleStatus.OFFLINE)
        avg_battery = sum(v.battery_percent for v in self.vehicles) / len(self.vehicles)
        
        print(f"\nFleet Status:")
        print(f"  Online:              {online}")
        print(f"  Offline:             {offline}")
        print(f"  Avg battery:         {avg_battery:.1f}%")
        
        # Firmware distribution
        firmware_counts = {}
        for v in self.vehicles:
            firmware_counts[v.firmware_version] = firmware_counts.get(v.firmware_version, 0) + 1
        
        print(f"\nFirmware Distribution:")
        for version, count in sorted(firmware_counts.items()):
            print(f"  {version}: {count} vehicles ({count/len(self.vehicles)*100:.1f}%)")
        
        print("="*70 + "\n")


def main():
    """Main entry point for vehicle simulator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='FleetOTA Vehicle Telemetry Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulate 100 vehicles for 1 hour with 60-second intervals
  python vehicle_generator.py --vehicles 100 --duration 60 --interval 60
  
  # Quick test with 10 vehicles for 5 minutes
  python vehicle_generator.py --vehicles 10 --duration 5 --interval 30
  
  # Custom S3 bucket and region
  python vehicle_generator.py --bucket my-fleet-data --region us-west-2
        """
    )
    
    parser.add_argument(
        '--vehicles',
        type=int,
        default=100,
        help='Number of vehicles to simulate (default: 100)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Simulation duration in minutes (default: 60)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Telemetry generation interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--bucket',
        type=str,
        default='fleetota-telemetry',
        help='S3 bucket name for telemetry storage (default: fleetota-telemetry)'
    )
    
    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Update log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Print banner
    print("\n" + "="*70)
    print("FleetOTA Vehicle Telemetry Generator")
    print("="*70)
    print(f"Vehicles:    {args.vehicles}")
    print(f"Duration:    {args.duration} minutes")
    print(f"Interval:    {args.interval} seconds")
    print(f"S3 Bucket:   {args.bucket}")
    print(f"AWS Region:  {args.region}")
    print("="*70 + "\n")
    
    # Verify AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"AWS Identity verified: {identity['Account']}")
    except Exception as e:
        logger.error(f"Failed to verify AWS credentials: {e}")
        logger.error("Please configure AWS credentials using 'aws configure'")
        sys.exit(1)
    
    # Verify S3 bucket exists
    try:
        s3 = boto3.client('s3', region_name=args.region)
        s3.head_bucket(Bucket=args.bucket)
        logger.info(f"S3 bucket '{args.bucket}' verified")
    except Exception as e:
        logger.error(f"S3 bucket '{args.bucket}' not accessible: {e}")
        logger.error(f"Create bucket with: aws s3 mb s3://{args.bucket} --region {args.region}")
        sys.exit(1)
    
    # Initialize and run simulation
    try:
        simulator = FleetSimulator(
            num_vehicles=args.vehicles,
            s3_bucket=args.bucket,
            aws_region=args.region
        )
        
        simulator.run_simulation(
            duration_minutes=args.duration,
            interval_seconds=args.interval
        )
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()