from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password
from .utils.contact_validation import ContactNumberValidator
from .utils.email_validation import EmailValidator
from .utils.username_validation import UsernameValidator
import re
import random
import string

# Name validation with specific field rules
def validate_name(value):
    """
    Name validation for First Name and Last Name fields:
    - Allowed Characters: A-Z and a-z only
    - Maximum Identical Letter Repetition: 3 consecutive
    - Consecutive Vowel Limit: 4 standard, 5 if all unique
    - Maximum Name Length: 50 characters
    - Maximum Total Letter Repetition: 6 times per letter in entire name
    """
    if not value or not value.strip():
        raise ValidationError('Please enter a valid name.')
    
    value = value.strip()
    
    # Length Guard: Maximum 50 characters
    if len(value) < 2 or len(value) > 50:
        raise ValidationError('Please enter a valid name.')
    
    # Pattern Match: Only alphabetic characters A-Z and a-z
    if not re.match(r'^[a-zA-Z]+$', value):
        raise ValidationError('Please enter a valid name.')
    
    # Rule 1: Maximum Identical Letter Repetition - 3 consecutive
    if re.search(r'(.)\1{3,}', value, re.IGNORECASE):  # 4+ identical consecutive characters
        raise ValidationError('Please enter a valid name.')
    
    # Rule 2: Maximum Total Repetition of Any Letter Across Name - 6 times
    # Count occurrences of each letter in the entire name
    letter_counts = {}
    for char in value.lower():
        letter_counts[char] = letter_counts.get(char, 0) + 1
    
    # Check if any letter appears more than 6 times
    for letter, count in letter_counts.items():
        if count > 6:
            raise ValidationError('Please enter a valid name.')
    
    # Rule 2b: Detect spam patterns with multiple repeated letters
    # Block patterns like aaabbbcccdddeeefffggg where multiple letters are repeated
    repeated_letters = [letter for letter, count in letter_counts.items() if count >= 3]
    if len(repeated_letters) >= 3:  # 3+ different letters repeated 3+ times
        raise ValidationError('Please enter a valid name.')
    
    # Rule 3: Consecutive Vowel Limit - Standard rule (4 consecutive)
    vowel_match = re.search(r'[aeiouAEIOU]{4,}', value)
    if vowel_match:
        matched_sequence = vowel_match.group()
        
        # Rule 4: Unique Vowel Exception - 5 consecutive allowed only if all unique
        if len(matched_sequence) >= 5:
            # Check if all vowels are unique (case insensitive)
            vowels_lower = matched_sequence.lower()
            unique_vowels = set(vowels_lower)
            
            # If 5 vowels and all unique, it's allowed
            if len(matched_sequence) == 5 and len(unique_vowels) == 5:
                pass  # Allowed
            else:
                raise ValidationError('Please enter a valid name.')
        elif len(matched_sequence) > 4:
            # More than 5 vowels is never allowed
            raise ValidationError('Please enter a valid name.')
        # Exactly 4 vowels is allowed by standard rule
    
    # Rule 5: Reject obvious keyboard smash patterns (7+ identical consecutive characters)
    if re.search(r'(.)\1{6,}', value):
        raise ValidationError('Please enter a valid name.')

# Regex validator for Django model field
name_validator = RegexValidator(
    regex=r'^[a-zA-Z]+$',
    message='Please enter a valid name.',
    code='invalid_name'
)


class ClientFileUpload(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='file_uploads')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50, choices=[
        ('payment_receipt', 'Payment Receipt'),
        ('design_reference', 'Design Reference'),
        ('nail_art', 'Nail Art'),
        ('other', 'Other')
    ])
    upload_time = models.DateTimeField(auto_now_add=True)
    is_viewed_by_artist = models.BooleanField(default=False)
    reference_code = models.CharField(max_length=100, blank=True, null=True)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='upload_services')
    
    class Meta:
        ordering = ['-upload_time']
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.file_type} ({self.upload_time.strftime('%Y-%m-%d %H:%M')})"
    
    def get_file_type_display(self):
        choices = {
            'payment_receipt': 'Payment Receipt',
            'design_reference': 'Design Reference', 
            'nail_art': 'Nail Art',
            'other': 'Other'
        }
        return choices.get(self.file_type, self.file_type)

class FileUploadLog(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE, related_name='upload_logs')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='client_uploads')
    file_type = models.CharField(max_length=50, choices=[
        ('payment_receipt', 'Payment Receipt'),
        ('design_reference', 'Design Reference'),
        ('other', 'Other')
    ])
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    upload_time = models.DateTimeField(auto_now_add=True)
    is_viewed_by_artist = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-upload_time']
    
    def __str__(self):
        return f"{self.client.get_full_name()} - {self.file_type} ({self.upload_time.strftime('%Y-%m-%d %H:%M')})"
    
    def get_file_type_display(self):
        choices = {
            'payment_receipt': 'Payment Receipt',
            'design_reference': 'Design Reference',
            'other': 'Other'
        }
        return choices.get(self.file_type, self.file_type)


class ClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Client(AbstractBaseUser, PermissionsMixin):
    # From Finished Code
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    
    # From Unfinished Code (KEEP THESE)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    no_show_warnings = models.IntegerField(default=0)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ClientManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Added these since they are critical for your salon
    
    def clean(self):
        # Migrated Regex Validation Logic
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, self.email):
            raise ValidationError({'email': 'Enter a valid email address'})
        
        if self.contact_number and self.contact_number.strip():
            phone_regex = r'^\+?1?\d{9,15}$'
            if not re.match(phone_regex, self.contact_number):
                raise ValidationError({'contact_number': 'Enter a valid phone number'})
        
        name_regex = r"^[a-zA-Z\s\-']+$"
        if self.first_name and not re.match(name_regex, self.first_name):
            raise ValidationError({'first_name': 'First name can only contain letters, spaces, hyphens, and apostrophes'})
        
        if self.last_name and not re.match(name_regex, self.last_name):
            raise ValidationError({'last_name': 'Last name can only contain letters, spaces, hyphens, and apostrophes'})
    
    def get_full_name(self):
        """Return the client's full name (first + last)."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def public_display_name(self):
        first_name = (self.first_name or '').strip()
        last_name = (self.last_name or '').strip()

        if not first_name and not last_name:
            return 'Anonymous User'

        if not first_name:
            return f"{last_name[0]}." if last_name else 'Anonymous User'

        last_initial = f" {last_name[0]}." if last_name else ''
        return f"{first_name}{last_initial}"

    def get_short_name(self):
        """Return the client's short name (first name)."""
        return self.first_name

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()
    
    @classmethod
    def generate_otp(cls, email):
        cls.objects.filter(email=email, is_used=False).update(is_used=True)
        otp = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(email=email, otp=otp)
    
    def __str__(self):
        return f"OTP for {self.email}: {self.otp}"

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    category = models.CharField(
        max_length=20,
        choices=[
            ('gel_polish', 'Gel Polish'),
            ('extensions', 'Extensions'),
            ('soft_gel_extensions', 'Soft Gel Extensions'),
            ('removal', 'Removal'),
        ]
    )
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    features = models.JSONField(default=list, help_text="List of service features")
    badge = models.CharField(
        max_length=20,
        choices=[
            ('popular', 'Popular'),
            ('premium', 'Premium'),
            ('trending', 'Trending'),
            ('classic', 'Classic'),
            ('', 'None'),
        ],
        default='',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - ₱{self.price}"
    
    @classmethod
    def create_default_services(cls):
        """Create default services for the system"""
        default_services = [
            # ------------------------------------
            # CATEGORY: GEL POLISH
            # ------------------------------------
            {
                'name': 'Advanced Gel Polish',
                'description': 'Intricate gel polish designs with advanced techniques and detailed artwork for a sophisticated look.',
                'price': 1200.00,
                'duration': 90,
                'category': 'gel_polish',
                'features': ['Complex nail art techniques', 'Detailed hand-painted designs', 'Premium gel polish finish'],
                'badge': 'premium',
            },
            {
                'name': 'Full Set Gel Polish',
                'description': 'Complete gel polish application with perfect coverage and long-lasting glossy finish.',
                'price': 650.00,
                'duration': 60,
                'category': 'gel_polish',
                'features': ['Full color application', 'Chip-resistant finish', 'Includes basic nail shaping'],
                'badge': 'popular',
            },
            {
                'name': 'Minimal Gel Polish',
                'description': 'Simple, elegant gel polish application for a clean and natural look.',
                'price': 350.00,
                'duration': 45,
                'category': 'gel_polish',
                'features': ['Clean polish application', 'Natural look', 'Long-lasting finish'],
                'badge': 'classic',
            },
            {
                'name': 'Plain Gel Polish',
                'description': 'Basic single-color gel polish application for a simple, classic look.',
                'price': 300.00,
                'duration': 40,
                'category': 'gel_polish',
                'features': ['Single color application', 'Quick service', 'Durable finish'],
                'badge': 'classic',
            },

            # ------------------------------------
            # CATEGORY: EXTENSIONS
            # ------------------------------------
            {
                'name': 'Basic Extensions',
                'description': 'Classic acrylic extensions for durable length and strength.',
                'price': 800.00,
                'duration': 90,
                'category': 'extensions',
                'features': ['Strong acrylic application', 'Custom shape and length', 'Long-lasting wear'],
                'badge': 'classic',
            },
            {
                'name': 'Color Gel Extensions',
                'description': 'Extensions with vibrant gel color for a bold, eye-catching look.',
                'price': 1000.00,
                'duration': 100,
                'category': 'extensions',
                'features': ['Acrylic extensions', 'Gel color application', 'Durable finish'],
                'badge': 'popular',
            },
            {
                'name': 'French Tip Extensions',
                'description': 'Elegant French tip extensions for a timeless, sophisticated appearance.',
                'price': 950.00,
                'duration': 95,
                'category': 'extensions',
                'features': ['Classic French tips', 'Extension application', 'Clean white finish'],
                'badge': 'premium',
            },
            {
                'name': 'Nail Art Extensions',
                'description': 'Extensions with custom nail art designs for a unique, personalized look.',
                'price': 1300.00,
                'duration': 120,
                'category': 'extensions',
                'features': ['Extension application', 'Custom nail art', 'Detailed designs'],
                'badge': 'premium',
            },

            # ------------------------------------
            # CATEGORY: SOFT GEL EXTENSIONS
            # ------------------------------------
            {
                'name': 'Advanced Soft Gel Extensions',
                'description': 'Premium soft gel extensions with intricate designs and advanced techniques.',
                'price': 1400.00,
                'duration': 110,
                'category': 'soft_gel_extensions',
                'features': ['Soft gel tips', 'Advanced nail art', 'Flexible comfortable wear'],
                'badge': 'premium',
            },
            {
                'name': 'Full Soft Gel Extensions',
                'description': 'Complete soft gel extension set with perfect fit and natural feel.',
                'price': 1200.00,
                'duration': 100,
                'category': 'soft_gel_extensions',
                'features': ['Full soft gel application', 'Natural look', 'Lightweight feel'],
                'badge': 'popular',
            },
            {
                'name': 'Minimal Soft Gel Extensions',
                'description': 'Simple, elegant soft gel extensions for a natural enhancement.',
                'price': 1000.00,
                'duration': 90,
                'category': 'soft_gel_extensions',
                'features': ['Minimal extension', 'Soft gel application', 'Natural appearance'],
                'badge': 'classic',
            },

            # ------------------------------------
            # CATEGORY: REMOVAL
            # ------------------------------------
            {
                'name': 'Gel Removal',
                'description': 'Safe and gentle removal of gel polish without damaging natural nails.',
                'price': 150.00,
                'duration': 30,
                'category': 'removal',
                'features': ['Gentle gel removal', 'Nail protection', 'Cuticle care'],
                'badge': 'classic',
            }
        ]
        
        for service_data in default_services:
            cls.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )

class Artist(models.Model):
    user = models.OneToOneField(Client, on_delete=models.CASCADE, null=True, blank=True, help_text="Optional: Link to existing Client user for Django authentication")
    first_name = models.CharField(max_length=100, null=True, blank=True, help_text="Artist's first name")
    last_name = models.CharField(max_length=100, null=True, blank=True, help_text="Artist's last name")
    email = models.EmailField(unique=True, null=True, blank=True, help_text="Artist login email (unique)")
    password = models.CharField(max_length=128, blank=True, help_text="Hashed password for artist login")
    phone = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20, 
        default="Available",
        choices=[
            ('Available', 'Available'),
            ('Awaiting Client', 'Awaiting Client'),
            ('In Service', 'In Service'),
            ('Cleaning', 'Cleaning'),
        ]
    )
    is_active_employee = models.BooleanField(default=True)
    sanitation_until = models.DateTimeField(null=True, blank=True, help_text="When sanitation period ends")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        phone_regex = r'^\+?1?\d{9,15}$'
        if not re.match(phone_regex, self.phone):
            raise ValidationError({'phone': 'Enter a valid phone number'})
    
    def set_password(self, raw_password):
        """Set password using Django's password hashing"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password using Django's password verification"""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        # Auto-hash password if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Get artist's full name (from Artist model or linked Client user)"""
        if self.user:
            return self.user.get_full_name()
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    def get_first_name(self):
        """Get artist's first name (from Artist model or linked Client user)"""
        if self.user:
            return self.user.first_name
        return self.first_name or ""
    
    def get_email(self):
        """Get artist's email (from Artist model or linked Client user)"""
        if self.email:
            return self.email
        elif self.user:
            return self.user.email
        return ""
    
    def __str__(self):
        name = self.get_full_name()
        email = self.get_email()
        if name and email:
            return f"Artist: {name} ({email})"
        elif name:
            return f"Artist: {name}"
        elif email:
            return f"Artist: {email}"
        return f"Artist: {self.id}"
    
    @classmethod
    def create_demo_artist(cls):
        """Create demo artist account for development"""
        user, created = Client.objects.get_or_create(
            email='artist@demo.com',
            defaults={
                'first_name': 'Demo',
                'last_name': 'Artist',
                'contact_number': '+1234567890',
            }
        )
        if created:
            user.set_password('artist123')
            user.save()
        
        artist, artist_created = cls.objects.get_or_create(
            user=user,
            defaults={
                'email': 'artist@demo.com',
                'password': 'artist123',
                'phone': '+1234567890',
            }
        )
        if not artist_created:
            # Update existing artist to ensure email and password are set
            artist.email = 'artist@demo.com'
            artist.set_password('artist123')
            artist.phone = '+1234567890'
            artist.save()
        return artist

class ArtistAvailability(models.Model):
    """Store individual artist working hours and availability"""
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE, related_name='availability')
    
    # Daily working hours (24-hour format)
    monday_start = models.TimeField(null=True, blank=True, help_text="Start time for Monday (e.g., 09:00)")
    monday_end = models.TimeField(null=True, blank=True, help_text="End time for Monday (e.g., 18:00)")
    tuesday_start = models.TimeField(null=True, blank=True, help_text="Start time for Tuesday")
    tuesday_end = models.TimeField(null=True, blank=True, help_text="End time for Tuesday")
    wednesday_start = models.TimeField(null=True, blank=True, help_text="Start time for Wednesday")
    wednesday_end = models.TimeField(null=True, blank=True, help_text="End time for Wednesday")
    thursday_start = models.TimeField(null=True, blank=True, help_text="Start time for Thursday")
    thursday_end = models.TimeField(null=True, blank=True, help_text="End time for Thursday")
    friday_start = models.TimeField(null=True, blank=True, help_text="Start time for Friday")
    friday_end = models.TimeField(null=True, blank=True, help_text="End time for Friday")
    saturday_start = models.TimeField(null=True, blank=True, help_text="Start time for Saturday")
    saturday_end = models.TimeField(null=True, blank=True, help_text="End time for Saturday")
    sunday_start = models.TimeField(null=True, blank=True, help_text="Start time for Sunday")
    sunday_end = models.TimeField(null=True, blank=True, help_text="End time for Sunday")
    
    # Time slot interval in minutes
    slot_duration = models.PositiveIntegerField(default=60, help_text="Duration of each time slot in minutes")
    
    # Break times (optional)
    break_start = models.TimeField(null=True, blank=True, help_text="Daily break start time")
    break_end = models.TimeField(null=True, blank=True, help_text="Daily break end time")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Artist Availability"
        verbose_name_plural = "Artist Availabilities"
    
    def __str__(self):
        return f"Availability for {self.artist.get_full_name()}"
    
    def get_day_hours(self, day_of_week):
        """Get start and end hours for a specific day"""
        day_fields = {
            0: ('monday_start', 'monday_end'),      # Monday
            1: ('tuesday_start', 'tuesday_end'),    # Tuesday
            2: ('wednesday_start', 'wednesday_end'), # Wednesday
            3: ('thursday_start', 'thursday_end'),   # Thursday
            4: ('friday_start', 'friday_end'),       # Friday
            5: ('saturday_start', 'saturday_end'),   # Saturday
            6: ('sunday_start', 'sunday_end'),       # Sunday
        }
        
        start_field, end_field = day_fields.get(day_of_week, (None, None))
        
        if start_field and end_field:
            start_time = getattr(self, start_field)
            end_time = getattr(self, end_field)
            if start_time and end_time:
                return start_time, end_time
        
        return None, None
    
    def get_available_slots(self, date):
        """Get available time slots for a specific date"""
        from datetime import datetime, timedelta
        
        day_of_week = date.weekday()
        start_time, end_time = self.get_day_hours(day_of_week)
        
        if not start_time or not end_time:
            return []  # Artist not working on this day
        
        # Convert to datetime objects for calculation
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        # Generate time slots
        slots = []
        current_slot = start_datetime
        slot_delta = timedelta(minutes=self.slot_duration)
        
        while current_slot + slot_delta <= end_datetime:
            slot_time = current_slot.time()
            
            # Skip break times if configured
            if self.break_start and self.break_end:
                break_start_dt = datetime.combine(date, self.break_start)
                break_end_dt = datetime.combine(date, self.break_end)
                slot_end_dt = current_slot + slot_delta
                
                # Skip if slot overlaps with break time
                if not (slot_end_dt <= break_start_dt or current_slot >= break_end_dt):
                    current_slot += slot_delta
                    continue
            
            slots.append(slot_time.strftime('%H:%M'))
            current_slot += slot_delta
        
        return slots
    
    @classmethod
    def create_default_availability(cls, artist):
        """Create default availability for an artist (9 AM - 8 PM, Mon-Sat)"""
        default_hours = {
            'monday_start': '09:00',
            'monday_end': '20:00',
            'tuesday_start': '09:00', 
            'tuesday_end': '20:00',
            'wednesday_start': '09:00',
            'wednesday_end': '20:00',
            'thursday_start': '09:00',
            'thursday_end': '20:00',
            'friday_start': '09:00',
            'friday_end': '20:00',
            'saturday_start': '09:00',
            'saturday_end': '20:00',
            'sunday_start': None,  # Closed on Sunday
            'sunday_end': None,
            'slot_duration': 60,
            'break_start': '13:00',  # 1 PM break
            'break_end': '14:00',    # 2 PM break end
        }
        
        availability, created = cls.objects.get_or_create(
            artist=artist,
            defaults=default_hours
        )
        
        return availability

# -------------------------
# APPOINTMENT MODEL
# -------------------------
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Approved', 'Approved'),
        ('Rescheduling', 'Rescheduling'),
        ('On-going', 'On-going'),
        ('Finished', 'Finished'),
        ('Cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    previous_status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True, help_text="Stores the status before rescheduling was initiated")
    core_category = models.CharField(
        max_length=20,
        choices=[
            ('gel_polish', 'Gel Polish'),
            ('extensions', 'Extensions'),
            ('soft_gel_extensions', 'Soft Gel Extensions'),
            ('removal', 'Removal'),
        ],
        blank=True,
        null=True,
    )
    style_complexity = models.CharField(
        max_length=20,
        choices=[
            ('plain', 'Plain Gel Polish'),
            ('minimal', 'Minimal Set'),
            ('full', 'Full Set'),
            ('advanced', 'Advanced Set'),
            ('gel_polish_removal', 'Gel Polish Removal'),
            ('extensions_removal', 'Extensions Removal'),
        ],
        blank=True,
        null=True,
    )
    tip_length = models.CharField(max_length=10, blank=True)
    tip_shape = models.CharField(max_length=20, blank=True)
    tip_code = models.CharField(max_length=10, blank=True)
    has_custom_reference = models.BooleanField(default=False)
    design_reference_image = models.ImageField(upload_to='bookings/references/', blank=True, null=True)
    gallery_reference = models.ForeignKey('NailDesign', on_delete=models.SET_NULL, null=True, blank=True, related_name='referenced_appointments')
    builder_checklist = models.JSONField(default=dict, blank=True)
    estimated_work_minutes = models.PositiveIntegerField(default=0)
    cleanup_minutes = models.PositiveIntegerField(default=20)
    estimated_total_minutes = models.PositiveIntegerField(default=20)
    requires_double_slot = models.BooleanField(default=False)
    custom_art_description = models.CharField(max_length=500, blank=True)
    
    # --- NEW PAYMENT FIELDS ---
    reference_code = models.CharField(max_length=100, blank=True, null=True)
    payment_receipt = models.ImageField(upload_to='payment_receipts/', blank=True, null=True)

    # --- RESCHEDULE SOFT-LOCK FIELDS ---
    proposed_date = models.DateField(null=True, blank=True)
    proposed_time = models.TimeField(null=True, blank=True)
    reschedule_lock_expires_at = models.DateTimeField(null=True, blank=True)

    # --- SESSION TIMING FIELDS ---
    actual_start_time = models.DateTimeField(null=True, blank=True, help_text="When the session actually started")
    actual_end_time = models.DateTimeField(null=True, blank=True, help_text="When the session actually ended")
    overtime_duration = models.DurationField(null=True, blank=True, help_text="How long the session went over the scheduled time")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        client_name = self.client.first_name if self.client else "Deleted Client"
        return f"{self.service.name} - {client_name} ({self.date})"

class ServiceHistory(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='history')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='service_history')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_history')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        client_name = self.client.first_name if self.client else "Deleted Client"
        return f"{self.service.name} - {client_name} ({self.get_status_display()})"
    
    
class NailDesign(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='nail_designs/')
    tags = models.CharField(max_length=200, help_text="Comma-separated tags (e.g., minimalist, acrylic, gel, floral)")
    
    # NEW: Links the design to a specific service
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, help_text="Base service for this look")
    
    is_active = models.BooleanField(default=True, help_text="Show in AI recommender?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return ''

    @property
    def get_tag_list(self):
        """Splits the comma-separated tags into a clean list for the template."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    

class TwoFactorOTP(models.Model):
    user_email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    login_method = models.CharField(max_length=20, choices=[
        ('email', 'Email Login'),
        ('google', 'Google OAuth'),
        ('artist_email', 'Artist Email Login')
    ])
    user_type = models.CharField(max_length=10, choices=[
        ('client', 'Client'),
        ('artist', 'Artist')
    ], default='client')
    
    class Meta:
        ordering = ['-created_at']
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.created_at + timezone.timedelta(minutes=2)
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()
    
    @classmethod
    def generate_otp(cls, user_email, login_method, user_type='client'):
        import random
        import string
        # Invalidate any existing unused OTPs for this user
        cls.objects.filter(user_email=user_email, is_used=False).update(is_used=True)
        otp = ''.join(random.choices(string.digits, k=6))
        return cls.objects.create(user_email=user_email, otp=otp, login_method=login_method, user_type=user_type)
    
    def __str__(self):
        return f"2FA OTP for {self.user_email} ({self.login_method}, {self.user_type}): {self.otp}"


class Notification(models.Model):
    """Persistent in-app notification for bell icon popup."""
    recipient_email = models.EmailField(db_index=True)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient_email}: {self.message[:50]}"


class NailArtImageLibrary(models.Model):
    """Visual catalog used by the custom Nail Art selector."""
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to='nail_art_library/')
    style_key = models.CharField(max_length=80, unique=True)
    weight_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.weight_minutes}m)"


class ActivityLog(models.Model):
    """Track all user activities in the system."""
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('booking_created', 'Booking Created'),
        ('booking_updated', 'Booking Updated'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('booking_approved', 'Booking Approved'),
        ('booking_rescheduled', 'Booking Rescheduled'),
        ('booking_completed', 'Booking Completed'),
        ('profile_updated', 'Profile Updated'),
        ('password_changed', 'Password Changed'),
        ('password_reset', 'Password Reset'),
        ('file_uploaded', 'File Uploaded'),
        ('payment_uploaded', 'Payment Uploaded'),
        ('artist_status_changed', 'Artist Status Changed'),
        ('service_created', 'Service Created'),
        ('service_updated', 'Service Updated'),
        ('service_deleted', 'Service Deleted'),
        ('design_created', 'Design Created'),
        ('design_updated', 'Design Updated'),
        ('design_deleted', 'Design Deleted'),
        ('admin_action', 'Admin Action'),
        ('failed_login', 'Failed Login'),
        ('otp_generated', 'OTP Generated'),
        ('otp_verified', 'OTP Verified'),
        ('two_factor_enabled', 'Two Factor Enabled'),
        ('two_factor_disabled', 'Two Factor Disabled'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=[
            ('client', 'Client'),
            ('artist', 'Artist'),
            ('admin', 'Admin'),
            ('system', 'System'),
        ],
        default='client'
    )
    user = models.ForeignKey(
        Client, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs',
        help_text="Client user who performed the action"
    )
    artist = models.ForeignKey(
        Artist, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs',
        help_text="Artist who performed the action"
    )
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField(help_text="Detailed description of the activity")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the user")
    user_agent = models.TextField(blank=True, help_text="Browser/user agent information")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional related objects
    appointment = models.ForeignKey(
        'Appointment', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs'
    )
    service = models.ForeignKey(
        'Service', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='activity_logs'
    )
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional activity metadata")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user_type']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['user']),
            models.Index(fields=['artist']),
        ]
    
    def __str__(self):
        user_identifier = self.get_user_identifier()
        return f"{user_identifier} - {self.get_activity_type_display()} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
    
    def get_user_identifier(self):
        """Get a readable identifier for the user/artist who performed the action."""
        if self.user:
            return f"Client: {self.user.get_full_name()}"
        elif self.artist:
            return f"Artist: {self.artist.get_full_name()}"
        elif self.user_type == 'system':
            return "System"
        elif self.user_type == 'admin':
            return "Admin"
        return "Unknown User"
    
    @classmethod
    def log_activity(cls, user=None, artist=None, activity_type='', description='', 
                    ip_address=None, user_agent='', appointment=None, service=None, 
                    metadata=None, user_type='client'):
        """
        Create an activity log entry.
        
        Args:
            user: Client user object (for clients/admins)
            artist: Artist object (for artists)
            activity_type: Activity type from ACTIVITY_TYPES
            description: Human-readable description
            ip_address: User's IP address
            user_agent: Browser/user agent string
            appointment: Related appointment (if any)
            service: Related service (if any)
            metadata: Additional metadata as dict
            user_type: Type of user ('client', 'artist', 'admin', 'system')
        """
        return cls.objects.create(
            user=user,
            artist=artist,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            appointment=appointment,
            service=service,
            metadata=metadata or {},
            user_type=user_type
        )


class Review(models.Model):
    """Verified rating/review linked to a specific appointment."""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=500, blank=True)
    health_safety_flag = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    artist_reply = models.CharField(max_length=500, blank=True)
    artist_replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.appointment_id:
            if self.appointment.status != 'Finished':
                raise ValidationError('Reviews are only allowed for completed appointments.')
            if self.client_id and self.appointment.client_id != self.client_id:
                raise ValidationError('Review client must match the appointment client.')
            if self.artist_id and self.appointment.artist_id != self.artist_id:
                raise ValidationError('Review artist must match the appointment artist.')

    def save(self, *args, **kwargs):
        if self.appointment_id:
            self.is_verified = self.appointment.status == 'Finished'
            if not self.artist_id:
                self.artist = self.appointment.artist
        super().save(*args, **kwargs)

    @property
    def public_client_name(self):
        if not self.client:
            return 'Deleted User'
        return self.client.public_display_name

    def __str__(self):
        return f"Review #{self.pk} - {self.rating}★"


class ReviewEditLog(models.Model):
    """Audit trail for client review edits."""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='edit_logs')
    editor = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    old_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    old_comment = models.CharField(max_length=500, blank=True)
    old_health_safety_flag = models.BooleanField(default=False)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"ReviewEditLog for Review #{self.review_id} at {self.edited_at}"
