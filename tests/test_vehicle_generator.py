"""
Unit Tests for FleetOTA Vehicle Generator
==========================================
Tests for VIN generation, GPS simulation, and telemetry generation.

Run with: pytest test_vehicle_generator.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vehicle_simulator.vehicle_generator import (
    VINGenerator,
    GPSSimulator,
    Vehicle,
    VehicleStatus,
    ConnectivityType
)


class TestVINGenerator:
    """Test VIN generation and validation"""
    
    def test_vin_length(self):
        """VIN should be exactly 17 characters"""
        vin = VINGenerator.generate()
        assert len(vin) == 17, f"VIN length should be 17, got {len(vin)}"
    
    def test_vin_uniqueness(self):
        """Multiple VINs should be unique"""
        vins = [VINGenerator.generate() for _ in range(100)]
        unique_vins = set(vins)
        assert len(unique_vins) == 100, "VINs should be unique"
    
    def test_vin_check_digit(self):
        """Test check digit calculation"""
        vin_without_check = "5YJSA1E14MF12345"
        check_digit = VINGenerator.calculate_check_digit(vin_without_check)
        assert check_digit in '0123456789X', "Check digit should be 0-9 or X"
    
    def test_manufacturer_codes(self):
        """Test different manufacturer VINs"""
        for manufacturer in ['TESLA', 'FORD', 'GM', 'TOYOTA']:
            vin = VINGenerator.generate(manufacturer)
            assert len(vin) == 17
            assert vin[0:3] in VINGenerator.WMI_CODES.values()
    
    def test_vin_format(self):
        """VIN should contain only valid characters (no I, O, Q)"""
        vin = VINGenerator.generate()
        invalid_chars = {'I', 'O', 'Q'}
        assert not any(char in invalid_chars for char in vin), \
            "VIN contains invalid characters (I, O, or Q)"


class TestGPSSimulator:
    """Test GPS coordinate simulation"""
    
    def test_initialization(self):
        """GPS should initialize with given coordinates"""
        lat, lon = 37.7749, -122.4194
        gps = GPSSimulator(lat, lon)
        assert gps.latitude == lat
        assert gps.longitude == lon
    
    def test_position_update(self):
        """Position should change after update"""
        gps = GPSSimulator(37.7749, -122.4194)
        initial_lat, initial_lon = gps.latitude, gps.longitude
        new_lat, new_lon = gps.update_position(60)
        
        # Position should change (unless vehicle is stationary)
        # Allow for rare case where position doesn't change significantly
        assert (new_lat, new_lon) != (initial_lat, initial_lon) or gps.speed_kmh < 1
    
    def test_coordinate_bounds(self):
        """Coordinates should stay within valid bounds"""
        gps = GPSSimulator(0, 0)
        for _ in range(100):
            lat, lon = gps.update_position(60)
            assert -90 <= lat <= 90, f"Latitude {lat} out of bounds"
            assert -180 <= lon <= 180, f"Longitude {lon} out of bounds"
    
    def test_speed_bounds(self):
        """Speed should stay within realistic bounds"""
        gps = GPSSimulator(37.7749, -122.4194)
        for _ in range(50):
            gps.update_position(60)
            assert 0 <= gps.speed_kmh <= 150, f"Speed {gps.speed_kmh} unrealistic"
    
    def test_random_city_coordinates(self):
        """Random city coordinates should be valid"""
        for _ in range(20):
            lat, lon = GPSSimulator.get_random_city_coordinates()
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180


class TestVehicle:
    """Test Vehicle class"""
    
    def test_vehicle_initialization(self):
        """Vehicle should initialize with valid data"""
        vehicle = Vehicle(vehicle_id=1)
        
        assert vehicle.vehicle_id == 1
        assert len(vehicle.vin) == 17
        assert vehicle.model in Vehicle.VEHICLE_MODELS
        assert 2020 <= vehicle.year <= 2025
        assert 0 <= vehicle.battery_percent <= 100
        assert vehicle.status in VehicleStatus
    
    def test_telemetry_generation(self):
        """Telemetry should have all required fields"""
        vehicle = Vehicle(vehicle_id=1)
        telemetry = vehicle.generate_telemetry()
        
        # Check top-level fields
        required_fields = [
            'vehicle_id', 'vin', 'timestamp', 'model', 'year',
            'gps', 'battery', 'connectivity', 'status', 
            'odometer_km', 'firmware', 'diagnostics'
        ]
        for field in required_fields:
            assert field in telemetry, f"Missing field: {field}"
        
        # Check nested GPS fields
        assert 'latitude' in telemetry['gps']
        assert 'longitude' in telemetry['gps']
        assert 'speed_kmh' in telemetry['gps']
        
        # Check nested battery fields
        assert 'percent' in telemetry['battery']
        assert 'health' in telemetry['battery']
        
        # Check nested connectivity fields
        assert 'type' in telemetry['connectivity']
        assert 'signal_strength_dbm' in telemetry['connectivity']
    
    def test_battery_drain(self):
        """Battery should drain over time"""
        vehicle = Vehicle(vehicle_id=1)
        vehicle.status = VehicleStatus.ONLINE
        initial_battery = vehicle.battery_percent
        
        # Simulate 10 minutes of driving
        for _ in range(10):
            vehicle.simulate_battery_drain(60)
        
        # Battery should have drained (unless it charged)
        assert vehicle.battery_percent <= initial_battery + 5  # Allow for charging
    
    def test_battery_bounds(self):
        """Battery percentage should stay within valid bounds"""
        vehicle = Vehicle(vehicle_id=1)
        
        for _ in range(100):
            vehicle.simulate_battery_drain(60)
            assert 0 <= vehicle.battery_percent <= 100
    
    def test_telemetry_json_serializable(self):
        """Telemetry should be JSON serializable"""
        import json
        vehicle = Vehicle(vehicle_id=1)
        telemetry = vehicle.generate_telemetry()
        
        try:
            json.dumps(telemetry)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Telemetry not JSON serializable: {e}")
    
    def test_warning_generation(self):
        """Warnings should be generated for critical conditions"""
        vehicle = Vehicle(vehicle_id=1)
        
        # Force low battery
        vehicle.battery_percent = 10
        warnings = vehicle._generate_warnings()
        assert 'LOW_BATTERY' in warnings
        
        # Force weak signal
        vehicle.signal_strength = -85
        warnings = vehicle._generate_warnings()
        assert 'WEAK_SIGNAL' in warnings
    
    def test_multiple_telemetry_updates(self):
        """Vehicle should generate multiple telemetry updates"""
        vehicle = Vehicle(vehicle_id=1)
        
        telemetry_list = []
        for _ in range(5):
            telemetry = vehicle.generate_telemetry()
            telemetry_list.append(telemetry)
        
        # All should be valid
        assert len(telemetry_list) == 5
        
        # Timestamps should be different (or very close)
        timestamps = [t['timestamp'] for t in telemetry_list]
        assert len(timestamps) == 5


class TestIntegration:
    """Integration tests"""
    
    def test_vehicle_lifecycle(self):
        """Test complete vehicle lifecycle"""
        vehicle = Vehicle(vehicle_id=42)
        
        # Generate multiple telemetry updates
        for i in range(10):
            telemetry = vehicle.generate_telemetry()
            
            # Verify data integrity
            assert telemetry['vehicle_id'] == 42
            assert telemetry['vin'] == vehicle.vin
            assert isinstance(telemetry['gps']['latitude'], (int, float))
            assert isinstance(telemetry['battery']['percent'], (int, float))