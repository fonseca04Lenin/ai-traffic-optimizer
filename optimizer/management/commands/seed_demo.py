"""
Usage: python manage.py seed_demo
Populates the database with realistic demo data so the app
looks fully operational right out of the box.
"""
from django.core.management.base import BaseCommand
from optimizer.models import Driver, Job, Route, RouteStop


DRIVERS = [
    {'name': 'Marcus Rivera',    'vehicle_type': 'van',   'phone': '(305) 555-0182', 'max_daily_distance': 180.0},
    {'name': 'Sarah Kowalski',   'vehicle_type': 'truck', 'phone': '(786) 555-0247', 'max_daily_distance': 250.0},
    {'name': 'Devon Thompson',   'vehicle_type': 'car',   'phone': '(954) 555-0391', 'max_daily_distance': 120.0},
]

JOBS = [
    # Miami area coordinates — realistic addresses
    {'customer_name': 'Bayside Market',       'address': '401 Biscayne Blvd, Miami, FL 33132',
     'lat': 25.7753, 'lng': -80.1851, 'service_type': 'delivery', 'priority': 'high',   'status': 'pending'},
    {'customer_name': 'Wynwood Arts Center',  'address': '2116 NW 2nd Ave, Miami, FL 33127',
     'lat': 25.8006, 'lng': -80.1993, 'service_type': 'delivery', 'priority': 'high',   'status': 'pending'},
    {'customer_name': 'Coral Gables Library', 'address': '3443 Segovia St, Coral Gables, FL 33134',
     'lat': 25.7488, 'lng': -80.2600, 'service_type': 'repair',   'priority': 'normal', 'status': 'pending'},
    {'customer_name': 'Little Havana Café',   'address': '1465 SW 8th St, Miami, FL 33135',
     'lat': 25.7668, 'lng': -80.2206, 'service_type': 'cleaning', 'priority': 'normal', 'status': 'pending'},
    {'customer_name': 'Brickell City Centre', 'address': '701 S Miami Ave, Miami, FL 33130',
     'lat': 25.7601, 'lng': -80.1936, 'service_type': 'pickup',   'priority': 'high',   'status': 'pending'},
    {'customer_name': 'Aventura Mall Drop',   'address': '19501 Biscayne Blvd, Aventura, FL 33180',
     'lat': 25.9567, 'lng': -80.1432, 'service_type': 'delivery', 'priority': 'low',    'status': 'pending'},
    {'customer_name': 'Doral Tech Park',      'address': '8200 NW 41st St, Doral, FL 33166',
     'lat': 25.8173, 'lng': -80.3360, 'service_type': 'inspection','priority': 'normal','status': 'in_progress'},
    {'customer_name': 'South Beach Residence','address': '1234 Ocean Dr, Miami Beach, FL 33139',
     'lat': 25.7799, 'lng': -80.1300, 'service_type': 'lawn_care','priority': 'low',    'status': 'completed'},
]


class Command(BaseCommand):
    help = 'Seed the database with demo drivers and jobs'

    def handle(self, *args, **options):
        if Driver.objects.exists():
            self.stdout.write('Demo data already exists — skipping.')
            return

        # Create drivers
        drivers = []
        for d in DRIVERS:
            drivers.append(Driver.objects.create(**d))
        self.stdout.write(f'Created {len(drivers)} drivers.')

        # Create jobs
        jobs = []
        for i, j in enumerate(JOBS):
            job = Job.objects.create(
                customer_name=j['customer_name'],
                address=j['address'],
                latitude=j['lat'],
                longitude=j['lng'],
                service_type=j['service_type'],
                priority=j['priority'],
                status=j['status'],
                driver=drivers[i % len(drivers)] if i % 3 != 0 else None,
            )
            jobs.append(job)
        self.stdout.write(f'Created {len(jobs)} jobs.')

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
