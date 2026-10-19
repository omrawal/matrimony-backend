import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from profiles.models import CustomUser

# ---------------------------------------------------------------------------
# Realistic dummy data pools
# ---------------------------------------------------------------------------

MALE_FIRST_NAMES = [
    'Aarav', 'Vikram', 'Rohan', 'Karan', 'Siddharth',
    'Aditya', 'Rahul', 'Nikhil', 'Arjun', 'Varun',
    'Pranav', 'Kunal', 'Sahil', 'Dhruv', 'Ishaan',
    'Aakash', 'Rajesh', 'Sanjay', 'Manish', 'Deepak',
]

FEMALE_FIRST_NAMES = [
    'Ananya', 'Priya', 'Sneha', 'Kavya', 'Pooja',
    'Divya', 'Neha', 'Ritu', 'Aisha', 'Meera',
    'Tanvi', 'Ishita', 'Shreya', 'Pallavi', 'Riya',
    'Kritika', 'Anjali', 'Sunita', 'Reena', 'Swati',
]

LAST_NAMES = [
    'Sharma', 'Patel', 'Reddy', 'Iyer', 'Nair',
    'Gupta', 'Mehta', 'Joshi', 'Kulkarni', 'Chopra',
    'Rao', 'Mishra', 'Verma', 'Kapoor', 'Bansal',
    'Desai', 'Malhotra', 'Saxena', 'Trivedi', 'Pillai',
]

CASTS = [
    'Brahmin', 'Kshatriya', 'Vaishya', 'Shudra',
    'Bhat Brahmin', 'Iyer', 'Nair', 'Reddy',
    'Patel', 'Jain', 'Maratha', 'Kunbi',
    'Any', 'Any',
]

CITIES = [
    'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai',
    'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow',
    'Indore', 'Nagpur', 'Coimbatore', 'Visakhapatnam', 'Chandigarh',
]

EDUCATION_LEVELS = [
    'B.Tech / B.E.', 'M.Tech / M.S.', 'MBA / PGDM',
    'MBBS', 'BDS', 'LLB', 'CA / CMA',
    'B.Com', 'M.A. (History)', 'B.Sc. (Physics)',
    'Ph.D. (Computer Science)', 'M.Sc. (Chemistry)',
]

PROFESSIONS_MALE = [
    'Software Engineer', 'Data Scientist', 'Civil Engineer',
    'Doctor (General Physician)', 'Chartered Accountant',
    'Product Manager', 'Investment Banker', 'Teacher',
    'Entrepreneur', 'Government Service (IAS)',
]

PROFESSIONS_FEMALE = [
    'Software Engineer', 'Doctor (Pediatrician)', 'UX Designer',
    'Chartered Accountant', 'Marketing Manager',
    'Research Scientist', 'Civil Engineer', 'Teacher (M.A.)',
    'Content Writer', 'Entrepreneur (F&B)',
]

COMPLEXIONS = ['Fair', 'Wheatish', 'Dusky', 'Dark']
DIETS = ['Vegetarian', 'Non-Veg', 'Eggetarian', 'Pure Veg']
DRINKS = ['Never', 'Occasionally', 'Socially']

HOBBIES = [
    'cricket', 'cooking', 'reading', 'yoga', 'photography',
    'traveling', 'music', 'painting', 'hiking', 'badminton',
    'chess', 'gardening', 'writing', 'baking', 'meditation',
]

BIO_TEMPLATES_MALE = [
    'Hardworking {profession} from {city}. Looking for a like-minded partner who values family and career. Enjoys {hobby} and long drives on weekends.',
    '{education} graduate, currently working as a {profession}. Simple lifestyle, fond of {hobby} and Indian classical music. Seeking a compatible match.',
    'A {profession} based in {city}. Family-oriented with a passion for {hobby}. Believes in mutual respect and growth.',
    'Born and raised in {city}, completed {education}. Work as a {profession}. Love {hobby}, traveling, and spending time with family.',
]

BIO_TEMPLATES_FEMALE = [
    'Soft-spoken and family-oriented. Completed {education} and work as a {profession} in {city}. Enjoys {hobby} and cooking traditional meals.',
    '{education} graduate, currently a {profession}. Love {hobby}, reading, and classical music. Looking for a partner who values equality and togetherness.',
    'A {profession} from {city}. Passionate about {hobby} and cultural programs. Seeking a kind, understanding, and ambitious life partner.',
    '{education} degree holder, working as a {profession}. Enjoy {hobby} and weekend getaways. Family comes first for me.',
]

MOBILE_PREFIXES = ['7', '8', '9', '6']
DEV_PASSWORD = 'password123'


def random_dob(min_age: int, max_age: int) -> date:
    today = date.today()
    min_dob = today - timedelta(days=max_age * 365 + 365)
    max_dob = today - timedelta(days=min_age * 365)
    delta = (max_dob - min_dob).days
    if delta <= 0:
        return today - timedelta(days=min_age * 365)
    return min_dob + timedelta(days=random.randint(0, delta))


def random_phone(used: set) -> str:
    while True:
        phone = random.choice(MOBILE_PREFIXES) + ''.join(
            random.choices('0123456789', k=9)
        )
        if phone not in used:
            used.add(phone)
            return phone


def random_height(gender: str) -> str:
    if gender == 'male':
        feet = random.randint(5, 6)
        inches = random.randint(0, 11) if feet < 6 else random.randint(0, 4)
    else:
        feet = random.randint(4, 5)
        inches = random.randint(1, 11) if feet < 5 else random.randint(0, 8)
    return str(feet) + chr(39) + str(inches) + chr(34)


def random_weight(gender: str) -> int:
    if gender == 'male':
        return random.randint(60, 88)
    return random.randint(48, 70)


def build_bio(gender: str, education: str, profession: str, city: str) -> str:
    templates = BIO_TEMPLATES_MALE if gender == 'male' else BIO_TEMPLATES_FEMALE
    template = random.choice(templates)
    return template.format(
        education=education,
        profession=profession,
        city=city,
        hobby=random.choice(HOBBIES),
    )


def make_unique_email(first: str, last: str, used: set) -> str:
    base = first.lower() + '.' + last.lower()
    while True:
        email = base + str(random.randint(1, 9999)) + '@example.com'
        if email not in used:
            used.add(email)
            return email


class Command(BaseCommand):
    help = 'Seed the database with dummy male and female users for development.'

    def add_arguments(self, parser):
        parser.add_argument('--male-count', type=int, default=20,
                            help='Number of male users to create (default: 20)')
        parser.add_argument('--female-count', type=int, default=20,
                            help='Number of female users to create (default: 20)')
        parser.add_argument('--reset', action='store_true',
                            help='Delete all existing non-superuser profiles before seeding.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Preview what would be created without writing to the database.')

    @transaction.atomic
    def handle(self, *args, **options):
        male_count = options['male_count']
        female_count = options['female_count']
        reset = options['reset']
        dry_run = options['dry_run']

        if reset and not dry_run:
            deleted, _ = CustomUser.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING(
                'Deleted %d existing non-superuser profile(s).' % deleted
            ))
        elif reset and dry_run:
            count = CustomUser.objects.filter(is_superuser=False).count()
            self.stdout.write(self.style.WARNING(
                '[dry-run] Would delete %d non-superuser profile(s).' % count
            ))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '[dry-run] Would create %d male + %d female users.' % (male_count, female_count)
            ))
            return

        used_phones = set(
            CustomUser.objects.exclude(phone_number__isnull=True)
            .values_list('phone_number', flat=True)
        )
        used_emails = set(
            CustomUser.objects.exclude(email__isnull=True)
            .values_list('email', flat=True)
        )

        created = []

        for gender, count in (('male', male_count), ('female', female_count)):
            first_names = MALE_FIRST_NAMES if gender == 'male' else FEMALE_FIRST_NAMES
            professions = PROFESSIONS_MALE if gender == 'male' else PROFESSIONS_FEMALE

            for _ in range(count):
                first = random.choice(first_names)
                last = random.choice(LAST_NAMES)
                city = random.choice(CITIES)
                education = random.choice(EDUCATION_LEVELS)
                profession = random.choice(professions)

                user = CustomUser(
                    first_name=first,
                    last_name=last,
                    email=make_unique_email(first, last, used_emails),
                    phone_number=random_phone(used_phones),
                    gender=gender,
                    date_of_birth=random_dob(25, 40),
                    time_of_birth='%02d:%s:00' % (
                        random.randint(5, 18),
                        random.choice(['00', '15', '30', '45'])
                    ),
                    place_of_birth=random.choice(CITIES),
                    height=random_height(gender),
                    weight=random_weight(gender),
                    complexion=random.choice(COMPLEXIONS),
                    cast=random.choice(CASTS),
                    location=city,
                    education=education,
                    profession=profession,
                    diet=random.choice(DIETS),
                    drink=random.choice(DRINKS),
                    astrology=random.choice(['Manglik', 'Non-Manglik', 'Non-Manglik', None]),
                    mother_name='Mrs. ' + last,
                    father_name='Mr. ' + random.choice(LAST_NAMES) + ' ' + last,
                    mother_contact=random_phone(used_phones),
                    father_contact=random_phone(used_phones),
                    address='%d, %s, %s' % (
                        random.randint(1, 300),
                        random.choice(['MG Road', 'Station Road', 'Park Street', 'Lake View', 'Temple Road']),
                        city
                    ),
                    bio=build_bio(gender, education, profession, city),
                    is_verified=random.random() < 0.6,
                    pref_location=random.choice(['Any', city, 'Nearby cities']),
                    pref_cast=random.choice(['Any', 'Brahmin', 'Kshatriya', 'Vaishya', 'Any']),
                )

                user.set_password(DEV_PASSWORD)
                user.save()

                created.append(user)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 90))
        self.stdout.write(self.style.SUCCESS(
            '  Seeded %d user(s): %d male, %d female' % (len(created), male_count, female_count)
        ))
        self.stdout.write(self.style.SUCCESS('=' * 90))
        self.stdout.write('')

        self.stdout.write('  %-12s %-28s %-8s %-5s %-16s %s' % (
            'Username', 'Name', 'Gender', 'Age', 'City', 'Password'
        ))
        self.stdout.write('  ' + '-' * 86)

        for u in created:
            name = u.first_name + ' ' + u.last_name
            age = str(u.age) if u.age is not None else '-'
            location = u.location or '-'
            self.stdout.write('  %-12s %-28s %-8s %-5s %-16s %s' % (
                u.username, name, u.gender, age, location, DEV_PASSWORD
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            '  All passwords are set to: %s' % DEV_PASSWORD
        ))
        self.stdout.write(self.style.SUCCESS(
            '  Note: pref_age_min / pref_age_max were auto-calculated from DOB.'
        ))
        self.stdout.write('')