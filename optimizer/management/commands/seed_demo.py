"""
Usage:
  python manage.py seed_demo          # skips if data exists
  python manage.py seed_demo --reset  # wipes and reseeds
"""
from django.core.management.base import BaseCommand
from optimizer.models import Driver, Job, Route, RouteStop


DRIVERS = [
    {'name': 'Marcus Rivera',    'vehicle_type': 'van',        'phone': '(305) 555-0182', 'max_daily_distance': 180.0, 'is_available': True},
    {'name': 'Sarah Kowalski',   'vehicle_type': 'truck',      'phone': '(786) 555-0247', 'max_daily_distance': 250.0, 'is_available': True},
    {'name': 'Devon Thompson',   'vehicle_type': 'car',        'phone': '(954) 555-0391', 'max_daily_distance': 120.0, 'is_available': True},
    {'name': 'Jordan Patel',     'vehicle_type': 'van',        'phone': '(402) 555-0114', 'max_daily_distance': 160.0, 'is_available': True},
    {'name': 'Keisha Monroe',    'vehicle_type': 'motorcycle', 'phone': '(402) 555-0278', 'max_daily_distance': 90.0,  'is_available': False},
]

JOBS = [
    # ── Miami, FL ────────────────────────────────────────────────────────────
    {
        'customer_name': 'Bayside Market',
        'address': '401 Biscayne Blvd, Miami, FL 33132',
        'lat': 25.7753, 'lng': -80.1851,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'Wynwood Arts Center',
        'address': '2116 NW 2nd Ave, Miami, FL 33127',
        'lat': 25.8006, 'lng': -80.1993,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'Coral Gables Library',
        'address': '3443 Segovia St, Coral Gables, FL 33134',
        'lat': 25.7488, 'lng': -80.2600,
        'service_type': 'repair', 'priority': 'normal', 'status': 'pending',
    },
    {
        'customer_name': 'Little Havana Café',
        'address': '1465 SW 8th St, Miami, FL 33135',
        'lat': 25.7668, 'lng': -80.2206,
        'service_type': 'cleaning', 'priority': 'normal', 'status': 'pending',
    },
    {
        'customer_name': 'Brickell City Centre',
        'address': '701 S Miami Ave, Miami, FL 33130',
        'lat': 25.7601, 'lng': -80.1936,
        'service_type': 'pickup', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'Aventura Mall Drop',
        'address': '19501 Biscayne Blvd, Aventura, FL 33180',
        'lat': 25.9567, 'lng': -80.1432,
        'service_type': 'delivery', 'priority': 'low', 'status': 'pending',
    },
    {
        'customer_name': 'Doral Tech Park',
        'address': '8200 NW 41st St, Doral, FL 33166',
        'lat': 25.8173, 'lng': -80.3360,
        'service_type': 'inspection', 'priority': 'normal', 'status': 'in_progress',
    },
    {
        'customer_name': 'South Beach Residence',
        'address': '1234 Ocean Dr, Miami Beach, FL 33139',
        'lat': 25.7799, 'lng': -80.1300,
        'service_type': 'lawn_care', 'priority': 'low', 'status': 'completed',
    },
    {
        'customer_name': 'Midtown Storage Facility',
        'address': '3000 N Miami Ave, Miami, FL 33127',
        'lat': 25.8076, 'lng': -80.1954,
        'service_type': 'pickup', 'priority': 'normal', 'status': 'pending',
    },
    {
        'customer_name': 'Overtown Medical Supply',
        'address': '1000 NW 3rd Ave, Miami, FL 33136',
        'lat': 25.7819, 'lng': -80.2013,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },

    # ── Omaha, NE ────────────────────────────────────────────────────────────
    {
        'customer_name': 'Old Market Hardware',
        'address': '1011 Howard St, Omaha, NE 68102',
        'lat': 41.2565, 'lng': -95.9345,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'Midtown Crossing Offices',
        'address': '3110 Dodge St, Omaha, NE 68131',
        'lat': 41.2594, 'lng': -95.9750,
        'service_type': 'repair', 'priority': 'normal', 'status': 'pending',
    },
    {
        'customer_name': 'Aksarben Village Gym',
        'address': '2121 S 67th St, Omaha, NE 68106',
        'lat': 41.2436, 'lng': -96.0297,
        'service_type': 'inspection', 'priority': 'low', 'status': 'pending',
    },
    {
        'customer_name': 'Benson District Café',
        'address': '6056 Maple St, Omaha, NE 68104',
        'lat': 41.2847, 'lng': -96.0194,
        'service_type': 'cleaning', 'priority': 'normal', 'status': 'pending',
    },
    {
        'customer_name': 'Millard Lawn Services HQ',
        'address': '13510 W Center Rd, Omaha, NE 68144',
        'lat': 41.2388, 'lng': -96.1100,
        'service_type': 'lawn_care', 'priority': 'low', 'status': 'pending',
    },
    {
        'customer_name': 'Bellevue Distribution Center',
        'address': '1000 Fort Crook Rd N, Bellevue, NE 68005',
        'lat': 41.1553, 'lng': -95.9261,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'West Omaha Medical Plaza',
        'address': '17001 Burke St, Omaha, NE 68118',
        'lat': 41.2722, 'lng': -96.1700,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'Papillion Town Hall',
        'address': '122 E 3rd St, Papillion, NE 68046',
        'lat': 41.1553, 'lng': -96.0442,
        'service_type': 'inspection', 'priority': 'normal', 'status': 'pending',
    },
    {
        'customer_name': 'North Downtown Warehouse',
        'address': '500 N 16th St, Omaha, NE 68102',
        'lat': 41.2651, 'lng': -95.9389,
        'service_type': 'pickup', 'priority': 'normal', 'status': 'in_progress',
    },
    {
        'customer_name': 'Regency Court Retail',
        'address': '10000 Regency Pkwy, Omaha, NE 68114',
        'lat': 41.2583, 'lng': -96.0789,
        'service_type': 'repair', 'priority': 'low', 'status': 'completed',
    },
    {
        'customer_name': 'Kiewit Building — UNO',
        'address': '6001 Dodge St, Omaha, NE 68182',
        'lat': 41.2553, 'lng': -96.0019,
        'service_type': 'delivery', 'priority': 'high', 'status': 'pending',
    },
    {
        'customer_name': 'University Village Dorms — UNO',
        'address': '1001 University Dr N, Omaha, NE 68182',
        'lat': 41.2608, 'lng': -95.9947,
        'service_type': 'delivery', 'priority': 'normal', 'status': 'pending',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with demo drivers and jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Wipe existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            RouteStop.objects.all().delete()
            Route.objects.all().delete()
            Job.objects.all().delete()
            Driver.objects.all().delete()
            self.stdout.write('Existing data cleared.')
        elif Driver.objects.exists():
            self.stdout.write('Demo data already exists — run with --reset to reload.')
            return

        drivers = [Driver.objects.create(**d) for d in DRIVERS]
        self.stdout.write(f'Created {len(drivers)} drivers.')

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
                driver=drivers[i % len(drivers)] if i % 4 != 0 else None,
            )
            jobs.append(job)
        self.stdout.write(f'Created {len(jobs)} jobs.')
        self.stdout.write(self.style.SUCCESS('Done.'))
