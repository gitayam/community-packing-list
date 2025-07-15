"""
Management command to populate military bases, schools, and training events.
Includes US military posts and overseas installations in Germany, Italy, Japan, and Korea.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from packing_lists.models import Base, School, PackingList


class Command(BaseCommand):
    help = 'Create default military bases, schools, and training events for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing military data before creating new',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing military data...'))
            Base.objects.filter(name__icontains='base').delete()
            Base.objects.filter(name__icontains='fort').delete()
            Base.objects.filter(name__icontains='camp').delete()
            School.objects.filter(name__icontains='school').delete()
            School.objects.filter(name__icontains='course').delete()
            PackingList.objects.filter(name__icontains='FTX').delete()
            PackingList.objects.filter(name__icontains='NTC').delete()
            PackingList.objects.filter(name__icontains='JRTC').delete()

        with transaction.atomic():
            # Create military bases
            self.create_us_bases()
            self.create_overseas_bases()
            
            # Create military schools and selection courses
            self.create_military_schools()
            self.create_selection_courses()
            
            # Create training event templates
            self.create_training_events()

        self.stdout.write(
            self.style.SUCCESS('Successfully created military data!')
        )

    def create_us_bases(self):
        """Create major US military installations"""
        self.stdout.write('Creating US military bases...')
        
        us_bases = [
            # Army - Major Installations
            ('Fort Liberty (Bragg)', 'Fayetteville, NC', 35.1418, -79.0059),
            ('Fort Moore (Benning)', 'Columbus, GA', 32.3520, -84.9466),
            ('Fort Eisenhower (Gordon)', 'Augusta, GA', 33.4235, -82.1274),
            ('Fort Cavazos (Hood)', 'Killeen, TX', 31.1348, -97.7831),
            ('Fort Bliss', 'El Paso, TX', 31.8484, -106.4270),
            ('Fort Stewart', 'Hinesville, GA', 31.8777, -81.6137),
            ('Fort Campbell', 'Hopkinsville, KY', 36.6687, -87.4653),
            ('Fort Leavenworth', 'Leavenworth, KS', 39.3498, -94.9172),
            ('Fort Sill', 'Lawton, OK', 34.6479, -98.4001),
            ('Fort Knox', 'Fort Knox, KY', 37.8914, -85.9631),
            ('Fort Riley', 'Manhattan, KS', 39.0997, -96.7973),
            ('Fort Drum', 'Watertown, NY', 44.0554, -75.7737),
            ('Fort Carson', 'Colorado Springs, CO', 38.7492, -104.7886),
            ('Fort Wainwright', 'Fairbanks, AK', 64.8349, -147.6430),
            ('Joint Base Lewis-McChord', 'Tacoma, WA', 47.1126, -122.5840),
            ('Fort Shafter', 'Honolulu, HI', 21.3294, -157.8782),
            ('Fort Johnson (Polk)', 'Leesville, LA', 31.0515, -93.2041),
            ('Fort Novosel (Rucker)', 'Daleville, AL', 31.3237, -85.7197),
            ('Fort Leonard Wood', 'Waynesville, MO', 37.7391, -92.1496),
            ('Fort Huachuca', 'Sierra Vista, AZ', 31.5503, -110.3447),
            
            # Marine Corps
            ('Camp Pendleton', 'Oceanside, CA', 33.3656, -117.4244),
            ('Camp Lejeune', 'Jacksonville, NC', 34.6713, -77.3403),
            ('Marine Corps Base Quantico', 'Quantico, VA', 38.5187, -77.3063),
            ('Marine Corps Recruit Depot Parris Island', 'Parris Island, SC', 32.3117, -80.6908),
            ('Marine Corps Recruit Depot San Diego', 'San Diego, CA', 32.6953, -117.1392),
            ('Marine Corps Base Camp Butler', 'Okinawa, Japan', 26.2729, 127.7669),
            ('Marine Corps Air Ground Combat Center', 'Twentynine Palms, CA', 34.2916, -116.1625),
            
            # Navy
            ('Naval Station Norfolk', 'Norfolk, VA', 36.9447, -76.3272),
            ('Naval Base San Diego', 'San Diego, CA', 32.6867, -117.1218),
            ('Naval Station Great Lakes', 'Great Lakes, IL', 42.3126, -87.8447),
            ('Naval Air Station Pensacola', 'Pensacola, FL', 30.3503, -87.3186),
            ('Naval Station Pearl Harbor', 'Pearl Harbor, HI', 21.3600, -157.9489),
            ('Naval Base Kitsap', 'Bremerton, WA', 47.5545, -122.7150),
            
            # Air Force
            ('Lackland Air Force Base', 'San Antonio, TX', 29.3847, -98.6204),
            ('Maxwell Air Force Base', 'Montgomery, AL', 32.3820, -86.3658),
            ('Wright-Patterson Air Force Base', 'Dayton, OH', 39.8261, -84.0484),
            ('Eglin Air Force Base', 'Valparaiso, FL', 30.4832, -86.5255),
            ('Nellis Air Force Base', 'Las Vegas, NV', 36.2361, -115.0347),
            ('Peterson Space Force Base', 'Colorado Springs, CO', 38.8144, -104.7003),
            ('MacDill Air Force Base', 'Tampa, FL', 27.8492, -82.5031),
            ('Davis-Monthan Air Force Base', 'Tucson, AZ', 32.1661, -110.8831),
            ('Joint Base Andrews', 'Camp Springs, MD', 38.8081, -76.8672),
            
            # Coast Guard
            ('Coast Guard Academy', 'New London, CT', 41.3651, -72.1097),
            ('Coast Guard Training Center Cape May', 'Cape May, NJ', 38.9687, -74.9687),
        ]
        
        created_count = 0
        for name, address, lat, lng in us_bases:
            base, created = Base.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'latitude': lat,
                    'longitude': lng
                }
            )
            if created:
                created_count += 1
                
        self.stdout.write(f'Created {created_count} US military bases')

    def create_overseas_bases(self):
        """Create major overseas military installations"""
        self.stdout.write('Creating overseas military bases...')
        
        overseas_bases = [
            # Germany
            ('Ramstein Air Base', 'Ramstein-Miesenbach, Germany', 49.4369, 7.6003),
            ('Spangdahlem Air Base', 'Spangdahlem, Germany', 49.9725, 6.6925),
            ('Kaiserslautern Military Community', 'Kaiserslautern, Germany', 49.4475, 7.7689),
            ('Grafenwoehr Training Area', 'Grafenwoehr, Germany', 49.6989, 11.9422),
            ('Hohenfels Training Area', 'Hohenfels, Germany', 49.2194, 11.8367),
            ('Stuttgart Military Community', 'Stuttgart, Germany', 48.7758, 9.1829),
            ('Ansbach Military Community', 'Ansbach, Germany', 49.3069, 10.5825),
            ('Wiesbaden Army Airfield', 'Wiesbaden, Germany', 50.0497, 8.3253),
            
            # Italy
            ('Naval Air Station Sigonella', 'Sigonella, Italy', 37.4017, 14.9239),
            ('Aviano Air Base', 'Aviano, Italy', 46.0311, 12.5956),
            ('Naval Support Activity Naples', 'Naples, Italy', 40.8218, 14.1958),
            ('Caserma Ederle (Vicenza)', 'Vicenza, Italy', 45.5619, 11.5422),
            ('Camp Darby', 'Livorno, Italy', 43.5489, 10.3103),
            
            # Japan
            ('Yokota Air Base', 'Fussa, Japan', 35.7486, 139.3478),
            ('Naval Air Facility Atsugi', 'Atsugi, Japan', 35.4547, 139.4519),
            ('Marine Corps Air Station Iwakuni', 'Iwakuni, Japan', 34.1444, 132.2356),
            ('Kadena Air Base', 'Kadena, Okinawa, Japan', 26.3558, 127.7681),
            ('Camp Foster', 'Ginowan, Okinawa, Japan', 26.2703, 127.7533),
            ('Camp Schwab', 'Nago, Okinawa, Japan', 26.6242, 128.0378),
            ('Naval Air Facility Misawa', 'Misawa, Japan', 40.7031, 141.3686),
            ('Camp Zama', 'Zama, Japan', 35.5169, 139.3947),
            
            # South Korea
            ('Osan Air Base', 'Pyeongtaek, South Korea', 37.0906, 127.0297),
            ('Yongsan Garrison', 'Seoul, South Korea', 37.5347, 126.9758),
            ('Camp Humphreys', 'Pyeongtaek, South Korea', 36.9669, 127.0656),
            ('Kunsan Air Base', 'Gunsan, South Korea', 35.9036, 126.6161),
            ('Camp Casey', 'Dongducheon, South Korea', 37.9011, 127.0525),
            ('Camp Red Cloud', 'Uijeongbu, South Korea', 37.7286, 127.0547),
        ]
        
        created_count = 0
        for name, address, lat, lng in overseas_bases:
            base, created = Base.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'latitude': lat,
                    'longitude': lng
                }
            )
            if created:
                created_count += 1
                
        self.stdout.write(f'Created {created_count} overseas military bases')

    def create_military_schools(self):
        """Create military schools and training institutions"""
        self.stdout.write('Creating military schools...')
        
        schools = [
            # Army Schools
            ('US Army Ranger School', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('US Army Airborne School', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('US Army Air Assault School', 'Fort Campbell, KY', 36.6687, -87.4653),
            ('US Army Pathfinder School', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('US Army Mountain Warfare School', 'Jericho, VT', 44.5106, -72.8092),
            ('US Army Arctic Warfare School', 'Fort Wainwright, AK', 64.8349, -147.6430),
            ('US Army Jungle Operations Training Course', 'Fort Sherman, Panama', 9.3547, -79.9750),
            ('US Army Sniper School', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('US Army Combat Engineer School', 'Fort Leonard Wood, MO', 37.7391, -92.1496),
            ('US Army Military Police School', 'Fort Leonard Wood, MO', 37.7391, -92.1496),
            ('US Army Intelligence School', 'Fort Eisenhower (Gordon), GA', 33.4235, -82.1274),
            ('US Army Signal School', 'Fort Eisenhower (Gordon), GA', 33.4235, -82.1274),
            ('US Army Cyber School', 'Fort Eisenhower (Gordon), GA', 33.4235, -82.1274),
            ('US Army Field Artillery School', 'Fort Sill, OK', 34.6479, -98.4001),
            ('US Army Armor School', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('US Army Infantry School', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('US Army Aviation School', 'Fort Novosel (Rucker), AL', 31.3237, -85.7197),
            ('US Army Warrant Officer Career College', 'Fort Novosel (Rucker), AL', 31.3237, -85.7197),
            
            # Special Operations Schools
            ('US Army Special Warfare School', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            ('US Army Civil Affairs School', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            ('US Army Psychological Operations School', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            ('US Army Special Operations Aviation School', 'Fort Campbell, KY', 36.6687, -87.4653),
            
            # Marine Corps Schools
            ('Marine Corps Combat Training', 'Camp Pendleton, CA', 33.3656, -117.4244),
            ('Marine Corps Infantry Training Battalion', 'Camp Pendleton, CA', 33.3656, -117.4244),
            ('Marine Corps School of Infantry (East)', 'Camp Lejeune, NC', 34.6713, -77.3403),
            ('Marine Corps Mountain Warfare Training Center', 'Bridgeport, CA', 38.2544, -119.2319),
            ('Marine Corps Martial Arts Program', 'Quantico, VA', 38.5187, -77.3063),
            
            # Navy Schools
            ('Naval Special Warfare Training Center', 'Coronado, CA', 32.6775, -117.1831),
            ('Naval Diving and Salvage Training Center', 'Panama City, FL', 30.2072, -85.6944),
            ('Naval Flight Training', 'Pensacola, FL', 30.3503, -87.3186),
            ('Naval Nuclear Power School', 'Charleston, SC', 32.9019, -80.0367),
            ('Naval Submarine School', 'Groton, CT', 41.3956, -72.0828),
            
            # Air Force Schools
            ('Air Force Basic Military Training', 'Lackland AFB, TX', 29.3847, -98.6204),
            ('Air Force Officer Candidate School', 'Maxwell AFB, AL', 32.3820, -86.3658),
            ('Air Force Pararescue School', 'Kirtland AFB, NM', 35.0400, -106.5483),
            ('Air Force Combat Control School', 'Pope Army Airfield, NC', 35.1708, -79.0147),
            ('Air Force Survival School (SERE)', 'Fairchild AFB, WA', 47.6158, -117.6564),
            ('Air Force Test Pilot School', 'Edwards AFB, CA', 34.9056, -117.8836),
            
            # Joint Schools
            ('Joint Special Operations University', 'MacDill AFB, FL', 27.8492, -82.5031),
            ('Defense Language Institute', 'Monterey, CA', 36.5946, -121.8750),
            ('Naval Postgraduate School', 'Monterey, CA', 36.5946, -121.8750),
            ('Air Force Institute of Technology', 'Wright-Patterson AFB, OH', 39.8261, -84.0484),
        ]
        
        created_count = 0
        for name, address, lat, lng in schools:
            school, created = School.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'latitude': lat,
                    'longitude': lng
                }
            )
            if created:
                created_count += 1
                
        self.stdout.write(f'Created {created_count} military schools')

    def create_selection_courses(self):
        """Create special operations selection courses as schools"""
        self.stdout.write('Creating selection courses...')
        
        selection_courses = [
            # Army Special Operations
            ('Special Forces Assessment and Selection (SFAS)', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            ('Ranger Assessment and Selection Program (RASP)', 'Fort Moore (Benning), GA', 32.3520, -84.9466),
            ('Civil Affairs Assessment and Selection', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            ('Psychological Operations Assessment and Selection (POAS)', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            ('Special Operations Aviation Assessment and Selection', 'Fort Campbell, KY', 36.6687, -87.4653),
            ('Delta Force Selection (CAG Assessment)', 'Fort Liberty (Bragg), NC', 35.1418, -79.0059),
            
            # Navy Special Operations
            ('Basic Underwater Demolition/SEAL (BUD/S)', 'Coronado, CA', 32.6775, -117.1831),
            ('SEAL Qualification Training (SQT)', 'Coronado, CA', 32.6775, -117.1831),
            ('Navy SWCC Selection', 'Coronado, CA', 32.6775, -117.1831),
            ('Navy EOD School', 'Eglin AFB, FL', 30.4832, -86.5255),
            
            # Air Force Special Operations
            ('Pararescue Indoctrination Course', 'Lackland AFB, TX', 29.3847, -98.6204),
            ('Combat Control Assessment and Selection', 'Lackland AFB, TX', 29.3847, -98.6204),
            ('Special Operations Weather Assessment', 'Keesler AFB, MS', 30.4119, -88.9244),
            ('Tactical Air Control Party Assessment', 'Lackland AFB, TX', 29.3847, -98.6204),
            
            # Marine Corps Special Operations
            ('Marine Corps Special Operations Assessment and Selection', 'Camp Pendleton, CA', 33.3656, -117.4244),
            ('Marine Corps Force Reconnaissance Assessment', 'Camp Pendleton, CA', 33.3656, -117.4244),
            ('Marine Corps Critical Skills Operator Assessment', 'Camp Lejeune, NC', 34.6713, -77.3403),
        ]
        
        created_count = 0
        for name, address, lat, lng in selection_courses:
            school, created = School.objects.get_or_create(
                name=name,
                defaults={
                    'address': address,
                    'latitude': lat,
                    'longitude': lng
                }
            )
            if created:
                created_count += 1
                
        self.stdout.write(f'Created {created_count} selection courses')

    def create_training_events(self):
        """Create training event packing list templates"""
        self.stdout.write('Creating training event templates...')
        
        # Get some bases for the training events
        ntc_base, _ = Base.objects.get_or_create(
            name='National Training Center (NTC)',
            defaults={
                'address': 'Fort Irwin, CA',
                'latitude': 35.2606,
                'longitude': -116.6394
            }
        )
            
        try:
            jrtc_base = Base.objects.filter(name__icontains='Johnson').first()
            if not jrtc_base:
                jrtc_base = Base.objects.get(name='Fort Johnson (Polk)')
        except Base.DoesNotExist:
            jrtc_base = Base.objects.get(name='Fort Johnson (Polk)')
            
        try:
            bragg_base = Base.objects.filter(name__icontains='Liberty').first()
            if not bragg_base:
                bragg_base = Base.objects.get(name='Fort Liberty (Bragg)')
        except Base.DoesNotExist:
            bragg_base = Base.objects.get(name='Fort Liberty (Bragg)')

        training_events = [
            # Combat Training Center Rotations
            {
                'name': 'NTC Rotation Packing List',
                'description': 'National Training Center (Mojave Desert) rotation packing list for mechanized/armored units',
                'base': ntc_base,
                'event_type': 'training'
            },
            {
                'name': 'JRTC Rotation Packing List', 
                'description': 'Joint Readiness Training Center (Louisiana) rotation for light infantry and special operations',
                'base': jrtc_base,
                'event_type': 'training'
            },
            {
                'name': 'Combat Training Center (CTC) Generic',
                'description': 'Generic packing list for combat training center rotations',
                'base': None,
                'event_type': 'training'
            },
            
            # Field Training Exercises
            {
                'name': 'FTX - Temperate Climate',
                'description': 'Field Training Exercise packing list for temperate climate conditions',
                'base': None,
                'event_type': 'training'
            },
            {
                'name': 'FTX - Desert Environment',
                'description': 'Field Training Exercise packing list for desert/arid environments',
                'base': None,
                'event_type': 'training'
            },
            {
                'name': 'FTX - Cold Weather',
                'description': 'Field Training Exercise packing list for cold weather/winter conditions',
                'base': None,
                'event_type': 'training'
            },
            {
                'name': 'FTX - Jungle/Tropical',
                'description': 'Field Training Exercise packing list for jungle/tropical environments',
                'base': None,
                'event_type': 'training'
            },
            {
                'name': 'FTX - Mountain/High Altitude',
                'description': 'Field Training Exercise packing list for mountain/high altitude operations',
                'base': None,
                'event_type': 'training'
            },
            
            # Deployment Types
            {
                'name': 'Deployment - Middle East/Southwest Asia',
                'description': 'Deployment packing list for Middle East/Southwest Asia operations',
                'base': None,
                'event_type': 'deployment'
            },
            {
                'name': 'Deployment - Europe/NATO',
                'description': 'Deployment packing list for European/NATO operations',
                'base': None,
                'event_type': 'deployment'
            },
            {
                'name': 'Deployment - Pacific Theater',
                'description': 'Deployment packing list for Pacific Theater operations',
                'base': None,
                'event_type': 'deployment'
            },
            {
                'name': 'Deployment - Africa (AFRICOM)',
                'description': 'Deployment packing list for African operations',
                'base': None,
                'event_type': 'deployment'
            },
            {
                'name': 'Deployment - Arctic/Cold Weather',
                'description': 'Deployment packing list for Arctic/extreme cold operations',
                'base': None,
                'event_type': 'deployment'
            },
            
            # Special Operations
            {
                'name': 'Special Operations - Direct Action',
                'description': 'Special operations direct action mission packing list',
                'base': bragg_base,
                'event_type': 'training'
            },
            {
                'name': 'Special Operations - Unconventional Warfare',
                'description': 'Special operations unconventional warfare mission packing list',
                'base': bragg_base,
                'event_type': 'training'
            },
            {
                'name': 'Special Operations - Foreign Internal Defense',
                'description': 'Special operations foreign internal defense mission packing list',
                'base': bragg_base,
                'event_type': 'training'
            },
            
            # Multi-National Exercises
            {
                'name': 'NATO Exercise',
                'description': 'NATO multinational exercise packing list',
                'base': None,
                'event_type': 'training'
            },
            {
                'name': 'Pacific Partnership Exercise',
                'description': 'Pacific partnership/alliance exercise packing list',
                'base': None,
                'event_type': 'training'
            },
        ]
        
        created_count = 0
        for event_data in training_events:
            packing_list, created = PackingList.objects.get_or_create(
                name=event_data['name'],
                defaults={
                    'description': event_data['description'],
                    'base': event_data['base'],
                    'event_type': event_data['event_type']
                }
            )
            if created:
                created_count += 1
                
        self.stdout.write(f'Created {created_count} training event templates')