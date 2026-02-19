"""
Sample Data Generator for Fleet Management System

Run this script to populate the database with sample data for testing:
    python manage.py shell < sample_data.py
Or:
    python manage.py shell
    >>> exec(open('sample_data.py').read())
"""

from datetime import datetime, timedelta
from random import randint, choice, uniform
from decimal import Decimal

from core.models import Vehicle, Driver, Trip, MaintenanceRecord, Alert


def generate_sample_data():
    """Generate sample fleet data"""

    print("Creating sample fleet data...")

    # Sample data
    vehicle_data = [
        {'vin': '1HGCM82633A123456', 'plate': 'ABC-1234', 'make': 'Ford', 'model': 'F-150', 'year': 2020, 'type': 'truck'},
        {'vin': '2T1BURHE1KC123456', 'plate': 'XYZ-5678', 'make': 'Toyota', 'model': 'Camry', 'year': 2021, 'type': 'sedan'},
        {'vin': '1GCEK19H4EB123456', 'plate': 'DEF-9012', 'make': 'Chevrolet', 'model': 'Silverado', 'year': 2019, 'type': 'truck'},
        {'vin': '1F1F15ZF5GF123456', 'plate': 'GHI-3456', 'make': 'RAM', 'model': '1500', 'year': 2022, 'type': 'truck'},
        {'vin': 'JM1BK343681123456', 'plate': 'JKL-7890', 'make': 'Mazda', 'model': 'CX-5', 'year': 2021, 'type': 'suv'},
        {'vin': '5YJ3E1EA8JF123456', 'plate': 'MNO-2345', 'make': 'Tesla', 'model': 'Model 3', 'year': 2023, 'type': 'sedan'},
        {'vin': 'WAUZZZF45KA123456', 'plate': 'PQR-6789', 'make': 'Audi', 'model': 'Q7', 'year': 2020, 'type': 'suv'},
        {'vin': '3VWD17AJ4KM123456', 'plate': 'STU-0123', 'make': 'Volkswagen', 'model': 'Atlas', 'year': 2022, 'type': 'suv'},
    ]

    driver_data = [
        {'name': 'John Smith', 'email': 'john.smith@example.com', 'license': 'DL123456', 'type': 'class_a'},
        {'name': 'Sarah Johnson', 'email': 'sarah.j@example.com', 'license': 'DL789012', 'type': 'class_b'},
        {'name': 'Mike Wilson', 'email': 'mike.w@example.com', 'license': 'DL345678', 'type': 'class_c'},
        {'name': 'Emily Davis', 'email': 'emily.d@example.com', 'license': 'DL901234', 'type': 'class_c'},
    ]

    # Create vehicles
    vehicles = []
    for data in vehicle_data:
        vehicle = Vehicle.objects.create(
            vin=data['vin'],
            plate=data['plate'],
            make=data['make'],
            model=data['model'],
            year=data['year'],
            vehicle_type=data['type'],
            purchase_date=datetime(2020, 1, 1).date() + timedelta(days=randint(0, 1000)),
            current_mileage=Decimal(str(randint(15000, 95000) + uniform(0, 99))),
            fuel_capacity=Decimal(str(randint(15, 30))),
            status='active'
        )
        vehicles.append(vehicle)
        print(f"Created vehicle: {vehicle.plate}")

    # Create drivers
    drivers = []
    for data in driver_data:
        driver = Driver.objects.create(
            name=data['name'],
            email=data['email'],
            license_number=data['license'],
            license_type=data['type'],
            license_expiry=datetime(2025, 12, 31).date(),
            status='active',
            hire_date=datetime(2022, 1, 1).date() + timedelta(days=randint(0, 500))
        )
        drivers.append(driver)
        print(f"Created driver: {driver.name}")

    # Create trips
    start_locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ']
    end_locations = ['Miami, FL', 'Seattle, WA', 'Boston, MA', 'Denver, CO', 'Atlanta, GA']

    for i in range(50):
        vehicle = choice(vehicles)
        driver = choice(drivers)
        distance = Decimal(str(randint(50, 500) + uniform(0, 99)))
        fuel_used = Decimal(str(float(distance) / uniform(15, 30)))  # 15-30 MPG

        start_date = datetime.now() - timedelta(days=randint(1, 365))
        end_date = start_date + timedelta(hours=randint(2, 12))

        Trip.objects.create(
            vehicle=vehicle,
            driver=driver,
            start_date=start_date,
            end_date=end_date,
            distance=distance,
            fuel_used=fuel_used,
            start_location=choice(start_locations),
            end_location=choice(end_locations),
            status='completed'
        )

    print(f"Created 50 trips")

    # Create maintenance records
    maintenance_types = ['routine', 'repair', 'inspection', 'preventive']
    descriptions = [
        'Oil change and filter replacement',
        'Brake pad replacement',
        'Tire rotation and alignment',
        'Engine tune-up',
        'Transmission service',
        'Air filter replacement',
        'Coolant flush',
        'Battery replacement'
    ]

    for vehicle in vehicles:
        # Add 2-5 maintenance records per vehicle
        for i in range(randint(2, 5)):
            mileage_at_service = vehicle.current_mileage - Decimal(str(randint(1000, 10000) * (i + 1)))

            MaintenanceRecord.objects.create(
                vehicle=vehicle,
                date=datetime.now() - timedelta(days=randint(30, 365) * (i + 1)),
                maintenance_type=choice(maintenance_types),
                mileage_at_service=mileage_at_service,
                cost=Decimal(str(randint(100, 1500) + uniform(0, 99))),
                description=choice(descriptions),
                severity=choice(['low', 'medium', 'high']),
                performed_by='Auto Service Center',
                next_maintenance_mileage=mileage_at_service + Decimal('5000')
            )

    print(f"Created maintenance records")

    # Update vehicle mileage based on trips
    for vehicle in vehicles:
        total_distance = vehicle.trip_set.aggregate(
            total=Sum('distance')
        )['total'] or Decimal('0')
        vehicle.current_mileage = Decimal('5000') + total_distance
        vehicle.save()

    print(f"\nSample data generation complete!")
    print(f"- {len(vehicles)} vehicles created")
    print(f"- {len(drivers)} drivers created")
    print(f"- 50 trips created")
    print(f"- Maintenance records created")
    print(f"\nYou can now login to the admin panel or visit the dashboard!")


def clear_data():
    """Clear all sample data"""
    print("Clearing all data...")
    Trip.objects.all().delete()
    MaintenanceRecord.objects.all().delete()
    Alert.objects.all().delete()
    Driver.objects.all().delete()
    Vehicle.objects.all().delete()
    print("All data cleared.")


# Run the generator
if __name__ == '__main__':
    from django.db.models import Sum

    # Uncomment to clear existing data first
    # clear_data()

    generate_sample_data()
