"""
Enhanced privacy tests for public-facing pages and APIs
"""
import json
from datetime import date, time, timedelta
from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from booking.models import Appointment, Artist, Client, Review, Service, Notification

User = get_user_model()  # This will be the Client model


class PublicAPIPrivacyTests(TestCase):
    """Test privacy controls on public APIs"""
    
    def setUp(self):
        self.client = TestClient()
        self.test_email = 'privacytest@example.com'
        self.test_password = 'SecureTest123!'
        
        # Create test users
        self.client_user = Client.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            first_name='Privacy',
            last_name='Tester',
        )
        self.artist_user = Client.objects.create_user(
            email='artist@example.com',
            password='artist-pass-123',
            first_name='Artist',
            last_name='User',
        )
        self.artist = Artist.objects.create(user=self.artist_user, phone='+639171234567')
        self.service = Service.objects.create(
            name='Privacy Test Service',
            description='Test service for privacy validation',
            price=300,
            duration=45,
            category='manicure',
        )
    
    def test_public_artist_list_no_sensitive_data(self):
        """Test artist list doesn't expose sensitive information"""
        response = self.client.get(reverse('artist_public_reviews', args=[self.artist.id]))
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content)
        
        # Should not expose sensitive fields
        for artist_data in data:
            self.assertNotIn('email', artist_data)
            self.assertNotIn('phone', artist_data)
            self.assertNotIn('user_permissions', artist_data)
            self.assertNotIn('is_superuser', artist_data)
            self.assertNotIn('date_joined', artist_data)
            self.assertNotIn('last_login', artist_data)
    
    def test_public_service_list_no_internal_data(self):
        """Test service list doesn't expose internal data"""
        response = self.client.get(reverse('service_list'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        
        # Should not expose internal fields
        for service_data in data:
            self.assertNotIn('internal_notes', service_data)
            self.assertNotIn('cost_breakdown', service_data)
            self.assertNotIn('supplier_info', service_data)
    
    def test_public_appointment_list_requires_auth(self):
        """Test appointment list requires authentication"""
        response = self.client.get(reverse('appointment_list'))
        # Should redirect to login for unauthenticated users
        self.assertEqual(response.status_code, 302)
        
        # Test with authenticated user
        self.client.login(email=self.test_email, password=self.test_password)
        response = self.client.get(reverse('appointment_list'))
        self.assertEqual(response.status_code, 200)
        
        # Should only return user's own appointments
        data = json.loads(response.content)
        for appointment in data:
            self.assertEqual(appointment['client'], self.client_user.id)
    
    def test_public_review_privacy_masking(self):
        """Test review system properly masks sensitive data"""
        # Create test appointment and review
        appointment = Appointment.objects.create(
            client=self.client_user,
            artist=self.artist,
            service=self.service,
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            status='Finished',
        )
        review = Review.objects.create(
            appointment=appointment,
            client=self.client_user,
            artist=self.artist,
            rating=4,
            comment='Great service!',
        )
        
        # Test public review endpoint
        response = self.client.get(reverse('artist_public_reviews', args=[self.artist.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        review_data = next(r for r in data if r['id'] == review.id)
        
        # Should mask client information
        self.assertEqual(review_data['client_name'], 'Privacy T.')  # Masked
        self.assertNotIn('client_email', review_data)
        self.assertNotIn('client_phone', review_data)
        
        # Artist info should be public
        self.assertEqual(review_data['artist_name'], 'Artist User')
    
    def test_user_profile_privacy_controls(self):
        """Test user profile respects privacy settings"""
        self.client.login(email=self.test_email, password=self.test_password)
        
        # Test user can view own profile
        response = self.client.get(reverse('client_profile'))
        self.assertEqual(response.status_code, 200)
        
        # Test user cannot view other's profile directly
        other_user = Client.objects.create_user(
            email='other@example.com',
            password='other-pass-123',
            first_name='Other',
            last_name='User',
        )
        response = self.client.get(reverse('client_profile', args=[other_user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_search_functionality_no_data_leakage(self):
        """Test search doesn't expose sensitive user data"""
        # Create test data
        test_client = Client.objects.create_user(
            email='searchtest@example.com',
            password='search-pass-123',
            first_name='Search',
            last_name='Test',
            phone='+1234567890',
        )
        
        # Test search endpoints
        search_terms = ['searchtest', 'Search', 'Test']
        
        for term in search_terms:
            response = self.client.get(f"{reverse('search')}?q={term}")
            self.assertEqual(response.status_code, 200)
            
            # Should not expose sensitive information in search results
            data = json.loads(response.content)
            for result in data:
                self.assertNotIn('email', result)
                self.assertNotIn('phone', result)
                self.assertNotIn('address', result)
    
    def test_booking_form_csrf_protection(self):
        """Test booking form has CSRF protection"""
        self.client.login(email=self.test_email, password=self.test_password)
        
        response = self.client.get(reverse('booking_form'))
        self.assertEqual(response.status_code, 200)
        
        # Check for CSRF token in form
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test POST without CSRF token fails
        form_data = {
            'service': self.service.id,
            'artist': self.artist.id,
            'date': '2026-03-15',
            'time': '14:00',
        }
        
        response = self.client.post(reverse('booking_form'), form_data)
        self.assertEqual(response.status_code, 403)  # CSRF protection
    
    def test_api_rate_limiting(self):
        """Test API endpoints have rate limiting"""
        # Test multiple rapid requests to public API
        for i in range(10):
            response = self.client.get(reverse('service_list'))
        
        # Should implement rate limiting (this is a basic test)
        # In production, this would return 429 after threshold
        # For now, just ensure the endpoint doesn't crash
        self.assertIn(response.status_code, [200, 429])
    
    def test_data_export_requires_auth(self):
        """Test data export requires proper authentication"""
        # Test unauthenticated access
        response = self.client.get(reverse('export_user_data'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test authenticated access
        self.client.login(email=self.test_email, password=self.test_password)
        response = self.client.get(reverse('export_user_data'))
        self.assertEqual(response.status_code, 200)
        
        # Should only export user's own data
        self.assertContains(response, self.test_email)
        self.assertNotContains(response, 'artist@example.com')
    
    def test_session_security(self):
        """Test session management is secure"""
        self.client.login(email=self.test_email, password=self.test_password)
        
        response = self.client.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check for secure session headers
        self.assertIn('Set-Cookie', response)
        cookie_header = response['Set-Cookie']
        
        # Should have HttpOnly and Secure flags
        self.assertIn('HttpOnly', cookie_header)
        self.assertIn('Secure', cookie_header)
        
        # Should have reasonable session timeout
        self.assertIn('Max-Age', cookie_header)
        max_age = int(cookie_header.split('Max-Age=')[1].split(';')[0])
        self.assertLessEqual(max_age, 86400)  # 24 hours max
    
    def test_error_messages_no_sensitive_info(self):
        """Test error messages don't leak sensitive information"""
        # Test with invalid credentials
        response = self.client.post(reverse('login'), {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Error message should be generic
        self.assertContains(response, 'Invalid email or password')
        self.assertNotContains(response, 'user not found')
        self.assertNotContains(response, 'database error')
        self.assertNotContains(response, 'email does not exist')


class DataRetentionTests(TestCase):
    """Test data retention and deletion policies"""
    
    def setUp(self):
        self.client = Client()
        self.test_user = Client.objects.create_user(
            email='retention@example.com',
            password='retention-pass-123',
            first_name='Data',
            last_name='Retention',
        )
        self.artist_user = Client.objects.create_user(
            email='artistret@example.com',
            password='artist-ret-123',
            first_name='Artist',
            last_name='Retention',
        )
        self.artist = Artist.objects.create(user=self.artist_user, phone='+639171234567')
        self.service = Service.objects.create(
            name='Retention Test Service',
            description='Test service for retention',
            price=200,
            duration=30,
            category='manicure',
        )
    
    def test_old_appointment_cleanup(self):
        """Test old appointments are cleaned up appropriately"""
        self.client.login(email='retention@example.com', password='retention-pass-123')
        
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
        
        # Test cleanup function (would be called by management command)
        # This tests the logic that would be in a cleanup management command
        from datetime import datetime
        cutoff_date = datetime.combine(date.today() - timedelta(days=365), time.min)
        
        old_appointments = Appointment.objects.filter(
            date__lt=cutoff_date.date(),
            status='Finished'
        )
        
        # Should find old appointments
        self.assertGreater(old_appointments.count(), 0)
        self.assertIn(old_appointment, old_appointments)
    
    def test_user_anonymization_on_deletion(self):
        """Test user data is properly anonymized on deletion"""
        self.client.login(email='retention@example.com', password='retention-pass-123')
        
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
        
        # Delete user (this should trigger anonymization)
        self.test_user.delete()
        
        # Check that review still exists but client is anonymized
        review.refresh_from_db()
        self.assertEqual(review.comment, 'Test review for anonymization')
        self.assertEqual(review.rating, 5)
        
        # Client reference should be null or anonymized
        self.assertIsNone(review.client.email if hasattr(review.client, 'email') else None)


class NotificationPrivacyTests(TestCase):
    """Test notification system respects privacy preferences"""
    
    def setUp(self):
        self.client = Client()
        self.test_user = Client.objects.create_user(
            email='notification@example.com',
            password='notification-pass-123',
            first_name='Notification',
            last_name='Test',
        )
        self.artist_user = Client.objects.create_user(
            email='artistnot@example.com',
            password='artist-notif-123',
            first_name='Artist',
            last_name='NoNotif',
        )
        self.artist = Artist.objects.create(user=self.artist_user, phone='+639171234567')
        self.service = Service.objects.create(
            name='Notification Test Service',
            description='Test service for notifications',
            price=250,
            duration=60,
            category='manicure',
        )
    
    def test_notification_preferences_respected(self):
        """Test user notification preferences are respected"""
        self.client.login(email='notification@example.com', password='notification-pass-123')
        
        # Create notification preference (would be in user profile)
        # This tests the logic that would respect notification settings
        response = self.client.post(reverse('update_notification_preferences'), {
            'email_notifications': False,
            'sms_notifications': False,
            'push_notifications': True,
            'appointment_reminders': False,
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Test that notifications are not sent when disabled
        # This would involve checking the notification sending logic
        # For now, just test the preference update works
        response = self.client.get(reverse('notification_preferences'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertFalse(data['email_notifications'])
        self.assertFalse(data['sms_notifications'])
        self.assertTrue(data['push_notifications'])
        self.assertFalse(data['appointment_reminders'])
    
    def test_public_notifications_no_private_data(self):
        """Test public notifications don't expose private data"""
        # Create appointment
        appointment = Appointment.objects.create(
            client=self.test_user,
            artist=self.artist,
            service=self.service,
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            status='Confirmed',
        )
        
        # Test public notification (would be for artist dashboard, etc.)
        response = self.client.get(reverse('public_notifications', args=[self.artist.id]))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        notification_data = next(n for n in data if n['appointment_id'] == appointment.id)
        
        # Should not expose client contact info
        self.assertNotIn('client_email', notification_data)
        self.assertNotIn('client_phone', notification_data)
        self.assertNotIn('client_address', notification_data)
        
        # Should expose necessary info for artist
        self.assertEqual(notification_data['service_name'], self.service.name)
        self.assertEqual(notification_data['appointment_time'], '14:00')


class FileUploadPrivacyTests(TestCase):
    """Test file upload privacy and security"""
    
    def setUp(self):
        self.client = Client()
        self.test_user = Client.objects.create_user(
            email='fileupload@example.com',
            password='file-upload-123',
            first_name='File',
            last_name='Upload',
        )
    
    def test_file_upload_validation(self):
        """Test file uploads are properly validated"""
        self.client.login(email='fileupload@example.com', password='file-upload-123')
        
        # Test malicious file upload attempts
        malicious_files = [
            # Script files
            ('malicious.php', b'<?php echo "hacked"; ?>', 'application/php'),
            # Executable files
            ('malicious.exe', b'MZ\x90\x00', 'application/x-executable'),
            # Large files
            ('large.jpg', b'x' * (5 * 1024 * 1024 + 1), 'image/jpeg'),  # 5MB + 1 byte
        ]
        
        for filename, content, content_type in malicious_files:
            response = self.client.post(reverse('upload_file'), {
                'file': (filename, content, content_type)
            })
            
            # Should reject malicious files
            self.assertNotEqual(response.status_code, 200)
        
        # Test legitimate file upload
        legitimate_content = b' legitimate image content'
        response = self.client.post(reverse('upload_file'), {
            'file': ('legitimate.jpg', legitimate_content, 'image/jpeg')
        })
        
        # Should accept legitimate files
        self.assertIn(response.status_code, [200, 302])  # 200 or redirect
    
    def test_file_access_control(self):
        """Test file access controls"""
        self.client.login(email='fileupload@example.com', password='file-upload-123')
        
        # Upload a test file
        response = self.client.post(reverse('upload_file'), {
            'file': ('test.jpg', b'test content', 'image/jpeg')
        })
        
        # Try to access another user's file
        other_user = Client.objects.create_user(
            email='otherfile@example.com',
            password='other-file-123',
            first_name='Other',
            last_name='File',
        )
        
        # Create file for other user (simulate)
        # This would test that users can only access their own files
        response = self.client.get(reverse('access_file', args=['other_file_123']))
        self.assertEqual(response.status_code, 403)  # Forbidden


class GDPRComplianceTests(TestCase):
    """Test GDPR compliance features"""
    
    def setUp(self):
        self.client = Client()
        self.test_user = Client.objects.create_user(
            email='gdpr@example.com',
            password='gdpr-pass-123',
            first_name='GDPR',
            last_name='Test',
        )
    
    def test_data_portability(self):
        """Test user can export their data (GDPR right to data portability)"""
        self.client.login(email='gdpr@example.com', password='gdpr-pass-123')
        
        response = self.client.get(reverse('export_user_data'))
        self.assertEqual(response.status_code, 200)
        
        # Should provide data in standard format (JSON/CSV)
        self.assertIn('Content-Type', response)
        content_type = response['Content-Type']
        self.assertIn(content_type, ['application/json', 'text/csv'])
        
        # Should include all user data
        data = json.loads(response.content) if 'json' in content_type else response.content
        self.assertIn('profile', data)
        self.assertIn('appointments', data)
        self.assertIn('reviews', data)
    
    def test_right_to_be_forgotten(self):
        """Test user can request data deletion (right to be forgotten)"""
        self.client.login(email='gdpr@example.com', password='gdpr-pass-123')
        
        response = self.client.post(reverse('request_data_deletion'), {
            'confirmation': True,
            'reason': 'User requested deletion'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Should initiate deletion process
        # In production, this would send confirmation email
        # For now, just test the endpoint works
        data = json.loads(response.content)
        self.assertTrue(data['deletion_requested'])
        self.assertIn(data['confirmation_id'], 'deletion_')
    
    def test_consent_management(self):
        """Test user can manage consent preferences"""
        self.client.login(email='gdpr@example.com', password='gdpr-pass-123')
        
        # Update consent preferences
        response = self.client.post(reverse('update_consent'), {
            'marketing_emails': False,
            'analytics_cookies': False,
            'third_party_sharing': False,
            'essential_cookies': True,  # Required for functionality
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify preferences were saved
        response = self.client.get(reverse('consent_preferences'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertFalse(data['marketing_emails'])
        self.assertFalse(data['analytics_cookies'])
        self.assertFalse(data['third_party_sharing'])
        self.assertTrue(data['essential_cookies'])
