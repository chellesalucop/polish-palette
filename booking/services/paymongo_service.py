import os
import requests
import json
import hmac
import hashlib
import base64
from django.conf import settings
from django.utils import timezone


class PayMongoService:
    def __init__(self):
        self.secret_key = settings.PAYMONGO_SECRET_KEY
        self.base_url = "https://api.paymongo.com/v1"
        # PayMongo requires base64 encoded "sk_test_xxx:" format
        credentials = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        }
    
    def create_checkout_session(self, amount, description, success_url, cancel_url, appointment=None, metadata=None):
        """Create a checkout session for payment"""
        data = {
            "data": {
                "attributes": {
                    "billing": {
                        "name": "Customer",
                        "email": "customer@example.com"
                    },
                    "send_email_receipt": True,
                    "show_description": True,
                    "show_line_items": True,
                    "line_items": [
                        {
                            "currency": "PHP",
                            "amount": int(amount * 100),  # Convert to cents
                            "description": description,
                            "name": "Nail Appointment",
                            "quantity": 1
                        }
                    ],
                    "payment_method_types": ["gcash", "paymaya", "card", "billease"],
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "description": description
                }
            }
        }
        
        if metadata:
            data["data"]["attributes"]["metadata"] = metadata
        elif appointment:
            # If appointment object is passed, create metadata from it
            appointment_metadata = {
                'appointment_id': str(appointment.id),
                'service_category': getattr(appointment, 'core_category', ''),
                'complexity_level': getattr(appointment, 'style_complexity', '')
            }
            if metadata:
                appointment_metadata.update(metadata)
            data["data"]["attributes"]["metadata"] = appointment_metadata
        
        response = requests.post(
            f"{self.base_url}/checkout_sessions",
            json=data,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"PayMongo API Error: {response.text}")
        
        return response.json()
    
    def retrieve_checkout_session(self, session_id):
        """Retrieve checkout session details"""
        response = requests.get(
            f"{self.base_url}/checkout_sessions/{session_id}",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"PayMongo API Error: {response.text}")
        
        return response.json()
    
    def verify_webhook_signature(self, payload, signature_header):
        """Verify webhook signature"""
        if not hasattr(settings, 'PAYMONGO_WEBHOOK_SECRET'):
            return False
        
        webhook_secret = settings.PAYMONGO_WEBHOOK_SECRET
        
        # Parse the signature header
        parts = signature_header.split(',')
        timestamp = None
        signature = None
        
        for part in parts:
            part = part.strip()
            if part.startswith('t='):
                timestamp = part[2:]
            elif part.startswith('v1='):
                signature = part[3:]
        
        if not timestamp or not signature:
            return False
        
        # Create the signed payload
        signed_payload = f"{timestamp}.{payload}"
        
        # Create expected signature
        expected_signature = hmac.new(
            webhook_secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(expected_signature, signature)
