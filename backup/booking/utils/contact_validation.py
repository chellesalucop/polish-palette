"""
Contact Number Validation Utility
E.164 International Standard Implementation
"""

import re
from django.core.exceptions import ValidationError


class ContactNumberValidator:
    """
    Utility class for validating and sanitizing phone numbers using E.164 standard
    """
    
    # Country codes and their expected subscriber number lengths
    COUNTRY_CONFIGS = {
        'PH': {
            'name': 'Philippines',
            'country_code': '63',
            'subscriber_length': 10,
            'valid_prefixes': [
                '917', '918', '919', '905', '906', '915', '916', '926', '927',
                '920', '921', '928', '929', '939', '948', '949',
                '951', '952', '953', '954', '955', '956',
                '907', '908', '909', '910', '911', '912', '913', '914',
                '990', '991', '992', '993', '994',
                '934', '935', '936', '937', '938',
                '940', '941', '942', '943', '944', '945', '946', '947',
                '977', '978', '979', '980', '981', '982', '983', '984', '985', '986', '987', '988', '989',
                '995', '996', '997', '998', '999',
            ]
        },
        'US': {
            'name': 'United States',
            'country_code': '1',
            'subscriber_length': 10,
        },
        'GB': {
            'name': 'United Kingdom',
            'country_code': '44',
            'subscriber_length': 10,
        }
    }
    
    @staticmethod
    def sanitize_contact_number(number):
        """
        Sanitize contact number by removing all non-digit characters except leading +
        
        Args:
            number (str): Raw contact number input
            
        Returns:
            str: Cleaned numeric contact number (digits only, or +digits)
        """
        if not number:
            return ''
        
        # Remove all non-digit characters, but preserve leading +
        number_str = str(number).strip()
        if number_str.startswith('+'):
            # Preserve leading +, remove other non-digits
            return '+' + ''.join(filter(str.isdigit, number_str[1:]))
        else:
            # Remove all non-digit characters
            return ''.join(filter(str.isdigit, number_str))
    
    @staticmethod
    def to_e164(number, default_country='PH'):
        """
        Convert phone number to E.164 format
        
        Args:
            number (str): Phone number in any format
            default_country (str): Default country code (default: 'PH')
            
        Returns:
            str: Phone number in E.164 format (+[country_code][subscriber_number])
            
        Raises:
            ValidationError: If number cannot be converted to E.164
        """
        if not number:
            raise ValidationError('Phone number is required')
        
        # Sanitize first
        clean_number = ContactNumberValidator.sanitize_contact_number(number)
        
        # If already in E.164 format
        if clean_number.startswith('+'):
            return clean_number
        
        # Get country config
        country_config = ContactNumberValidator.COUNTRY_CONFIGS.get(default_country)
        if not country_config:
            raise ValidationError(f'Unsupported country code: {default_country}')
        
        country_code = country_config['country_code']
        subscriber_length = country_config['subscriber_length']
        
        # Handle Philippine numbers (special case for 09XX format)
        if default_country == 'PH':
            if clean_number.startswith('0') and len(clean_number) == 11:
                # Convert 09XXXXXXXXX to +639XXXXXXXXX
                subscriber = clean_number[1:]  # Remove leading 0
                return f'+{country_code}{subscriber}'
            elif len(clean_number) == subscriber_length:
                # Already in subscriber format (9XXXXXXXXX)
                return f'+{country_code}{clean_number}'
            else:
                raise ValidationError(
                    f'Invalid Philippine mobile number format. '
                    f'Expected 11 digits (09XXXXXXXXX) or {subscriber_length} digits (9XXXXXXXXX). '
                    f'Got {len(clean_number)} digits.'
                )
        
        # Handle other countries
        elif len(clean_number) == subscriber_length:
            return f'+{country_code}{clean_number}'
        else:
            raise ValidationError(
                f'Invalid phone number length for {country_config["name"]}. '
                f'Expected {subscriber_length} digits, got {len(clean_number)}.'
            )
    
    @staticmethod
    def validate_e164(number, default_country='PH'):
        """
        Validate phone number and convert to E.164 format
        
        Args:
            number (str): Phone number to validate
            default_country (str): Default country code (default: 'PH')
            
        Returns:
            str: Phone number in E.164 format
            
        Raises:
            ValidationError: If number is invalid
        """
        e164_number = ContactNumberValidator.to_e164(number, default_country)
        
        # Additional validation for Philippine mobile prefixes
        if default_country == 'PH':
            country_config = ContactNumberValidator.COUNTRY_CONFIGS['PH']
            subscriber = e164_number[3:]  # Remove +63
            
            if len(subscriber) >= 3:
                prefix = subscriber[:3]
                if prefix not in country_config['valid_prefixes']:
                    raise ValidationError(
                        f'Invalid Philippine mobile number prefix: 0{prefix}. '
                        f'Valid prefixes include: 09{country_config["valid_prefixes"][0]}, 09{country_config["valid_prefixes"][1]}, etc.'
                    )
        
        # Check E.164 length constraints (max 15 digits after +)
        if len(e164_number) > 16:  # + + 15 digits
            raise ValidationError('Phone number too long. Maximum 15 digits allowed in E.164 format.')
        
        return e164_number
    
    @staticmethod
    def format_for_display(number, format_type='local'):
        """
        Format contact number for display purposes
        
        Args:
            number (str): Phone number in E.164 format or sanitized format
            format_type (str): 'local' for local format, 'international' for +63 format, 'e164' for E.164
            
        Returns:
            str: Formatted contact number
        """
        if not number:
            return number
        
        # Ensure we have E.164 format first
        if not number.startswith('+'):
            try:
                e164_number = ContactNumberValidator.to_e164(number)
            except ValidationError:
                return number  # Return as-is if can't convert
        else:
            e164_number = number
        
        if format_type == 'e164':
            return e164_number
        
        # Extract country code and subscriber
        if e164_number.startswith('+63'):
            subscriber = e164_number[3:]  # Remove +63
            
            if format_type == 'local':
                # Format: 09XXXXXXXXX
                return f'0{subscriber}'
            elif format_type == 'international':
                # Format: +63-9XX-XXX-XXXX
                if len(subscriber) == 10:
                    return f'+63-{subscriber[:3]}-{subscriber[3:6]}-{subscriber[6:]}'
                else:
                    return f'+63-{subscriber}'
        
        # For other countries, return E.164 or basic format
        if format_type == 'local':
            return e164_number[1:]  # Remove +
        else:
            return e164_number
    
    @staticmethod
    def normalize_for_storage(number, default_country='PH'):
        """
        Normalize contact number for database storage
        Stores in E.164 format (+[country_code][subscriber_number])
        
        Args:
            number (str): Contact number to normalize
            default_country (str): Default country code (default: 'PH')
            
        Returns:
            str: Normalized contact number in E.164 format
        """
        return ContactNumberValidator.validate_e164(number, default_country)
    
    @staticmethod
    def get_country_from_e164(e164_number):
        """
        Extract country information from E.164 number
        
        Args:
            e164_number (str): Phone number in E.164 format
            
        Returns:
            dict: Country information or None if not found
        """
        if not e164_number or not e164_number.startswith('+'):
            return None
        
        # Try to match with known country codes
        for country_code, config in ContactNumberValidator.COUNTRY_CONFIGS.items():
            if e164_number.startswith(f'+{config["country_code"]}'):
                return {
                    'code': country_code,
                    'name': config['name'],
                    'country_code': config['country_code']
                }
        
        return None
    
    # Legacy method for backward compatibility
    @staticmethod
    def validate_philippine_mobile(number):
        """
        Legacy method - use validate_e164 instead
        Validates Philippine mobile number and converts to E.164
        
        Args:
            number (str): Contact number to validate
            
        Returns:
            str: Phone number in E.164 format
            
        Raises:
            ValidationError: If number is invalid
        """
        return ContactNumberValidator.validate_e164(number, 'PH')
