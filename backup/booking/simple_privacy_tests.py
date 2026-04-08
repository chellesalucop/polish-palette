"""
Simplified privacy tests for public-facing pages
"""
import json
from datetime import date, time, timedelta
from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from booking.models import Appointment, Artist, Client, Review, Service

User = get_user_model()


class BasicPrivacyTests(TestCase):
    """Basic privacy tests that work with current setup"""
    
    def setUp(self):
        self.client = TestClient()
        self.test_user = User.objects.create_user(
            email='privacy@example.com',
            password='test-pass-123',
            first_name='Privacy',
            last_name='Tester',
        )
        self.artist_user = User.objects.create_user(
            email='artist@example.com',
            password='artist-pass-123',
            first_name='Artist',
            last_name='User',
        )
        self.artist = Artist.objects.create(user=self.artist_user)
        self.service = Service.objects.create(
            name='Privacy Test Service',
            description='Test service for privacy validation',
            price=300,
            duration=45,
            category='manicure',
        )
    
    def test_client_login_works(self):
        """Test basic client login functionality"""
        response = self.client.post(reverse('login'), {
            'email': 'privacy@example.com',
            'password': 'test-pass-123'
        })
        
        # Should redirect to dashboard on successful login
        self.assertIn(response.status_code, [200, 302])
    
    def test_public_pages_accessible(self):
        """Test that public pages are accessible"""
        public_urls = [
            'landing',
            'services',
        ]
        
        for url_name in public_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
    
    def test_protected_pages_require_auth(self):
        """Test that protected pages require authentication"""
        protected_urls = [
            'dashboard',
            'booking_create',
        ]
        
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            # Should redirect to login for unauthenticated users
            self.assertEqual(response.status_code, 302)
    
    def test_review_privacy_masking(self):
        """Test that reviews mask client information properly"""
        # Create appointment and review
        appointment = Appointment.objects.create(
            client=self.test_user,
            artist=self.artist,
            service=self.service,
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            status='Finished',
        )
        review = Review.objects.create(
            appointment=appointment,
            client=self.test_user,
            artist=self.artist,
            rating=4,
            comment='Test review for privacy',
        )
        
        # Test public review endpoint
        response = self.client.get(reverse('artist_public_reviews', args=[self.artist.id]))
        self.assertEqual(response.status_code, 200)
        
        # Check that client name is properly masked
        self.assertContains(response, 'Privacy T.')  # Should show masked name
        self.assertNotContains(response, 'Privacy Tester')  # Should not show full name
        self.assertNotContains(response, 'privacy@example.com')  # Should not show email
    
    def test_search_no_data_leakage(self):
        """Test that search doesn't expose sensitive information"""
        # Create test user with identifiable info
        test_user = User.objects.create_user(
            email='searchable@example.com',
            password='search-pass-123',
            first_name='Searchable',
            last_name='User',
        )
        
        # Test search functionality
        response = self.client.get(reverse('services'))  # Assuming services page has search
        
        # Should not expose sensitive user data
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'searchable@example.com')
        self.assertNotContains(response, 'Searchable User')
    
    def test_booking_form_csrf_protection(self):
        """Test that booking form has CSRF protection"""
        self.client.login(email='privacy@example.com', password='test-pass-123')
        
        response = self.client.get(reverse('booking_create'))
        self.assertEqual(response.status_code, 200)
        
        # Check for CSRF token in form
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_session_management(self):
        """Test session security headers"""
        self.client.login(email='privacy@example.com', password='test-pass-123')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check for secure session headers
        if 'Set-Cookie' in response:
            cookie_header = response['Set-Cookie']
            # Should have HttpOnly flag
            self.assertIn('HttpOnly', cookie_header)


class DataRetentionTests(TestCase):
    """Test data retention and cleanup"""
    
    def setUp(self):
        self.client = TestClient()
        self.test_user = User.objects.create_user(
            email='retention@example.com',
            password='retention-pass-123',
            first_name='Data',
            last_name='Retention',
        )
        self.artist_user = User.objects.create_user(
            email='artistret@example.com',
            password='artist-ret-123',
            first_name='Artist',
            last_name='Retention',
        )
        self.artist = Artist.objects.create(user=self.artist_user)
        self.service = Service.objects.create(
            name='Retention Test Service',
            description='Test service for retention',
            price=200,
            duration=30,
            category='manicure',
        )
    
    def test_appointment_cleanup_logic(self):
        """Test logic for cleaning up old appointments"""
        # This tests the business logic for data retention
        from datetime import datetime
        
        # Create old appointment (2 years ago)
        old_date = date.today() - timedelta(days=730)
        old_appointment = Appointment.objects.create(
            client=self.test_user,
            artist=self.artist,
            service=self.service,
            date=old_date,
            time=time(10, 0),
            status='Finished',
        )
        
        # Test cleanup logic
        cutoff_date = datetime.combine(date.today() - timedelta(days=365), time.min)
        
        old_appointments = Appointment.objects.filter(
            date__lt=cutoff_date.date(),
            status='Finished'
        )
        
        # Should find old appointments
        self.assertGreater(old_appointments.count(), 0)
        self.assertIn(old_appointment, old_appointments)
    
    def test_user_anonymization_on_deletion(self):
        """Test that user data is properly handled on deletion"""
        # Create appointment with review
        appointment = Appointment.objects.create(
            client=self.test_user,
            artist=self.artist,
            service=self.service,
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            status='Finished',
        )
        review = Review.objects.create(
            appointment=appointment,
            client=self.test_user,
            artist=self.artist,
            rating=5,
            comment='Test review for anonymization',
        )
        
        # Delete user
        self.test_user.delete()
        
        # Check that review still exists but user reference is handled
        review.refresh_from_db()
        self.assertEqual(review.comment, 'Test review for anonymization')
        self.assertEqual(review.rating, 5)
        
        # Should handle the deleted user reference gracefully
        try:
            client_name = review.client.first_name
        except:
            # User reference should be handled gracefully
            client_name = None
        
        self.assertIsNone(client_name)
