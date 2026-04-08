from datetime import date, time

from django.test import TestCase
from django.urls import reverse

from .models import Appointment, Artist, Client, Review, Service


class PublicReviewPrivacyTests(TestCase):
	def setUp(self):
		self.client_user = Client.objects.create_user(
			email='katherine@example.com',
			password='safe-pass-123',
			first_name='Katherine',
			last_name='Pierce',
		)
		self.artist_user = Client.objects.create_user(
			email='artist@example.com',
			password='safe-pass-123',
			first_name='Ariana',
			last_name='Cruz',
		)
		self.artist = Artist.objects.create(user=self.artist_user, phone='+639171234567')
		self.service = Service.objects.create(
			name='Gel Manicure',
			description='Long-lasting manicure service',
			price=500,
			duration=60,
			category='manicure',
		)
		self.appointment = Appointment.objects.create(
			client=self.client_user,
			artist=self.artist,
			service=self.service,
			date=date(2026, 3, 1),
			time=time(10, 0),
			status='Finished',
		)
		self.review = Review.objects.create(
			appointment=self.appointment,
			client=self.client_user,
			artist=self.artist,
			rating=5,
			comment='Excellent service and clean work.',
		)

	def test_public_review_uses_masked_client_name(self):
		response = self.client.get(reverse('artist_public_reviews', args=[self.artist.id]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Katherine P.')
		self.assertNotContains(response, 'Katherine Pierce')
		self.assertNotContains(response, 'katherine@example.com')

	def test_public_client_name_falls_back_to_masked_name_property(self):
		self.assertEqual(self.client_user.public_display_name, 'Katherine P.')
		self.assertEqual(self.review.public_client_name, 'Katherine P.')
