from django.core.exceptions import ValidationError
from django.utils import timezone
import re

def validate_positive_number(value, field_name):
    if value is not None and value <= 0:
        raise ValidationError({field_name: f'{field_name} must be a positive number.'})

def validate_year_of_manufacture(value):
    current_year = timezone.now().year
    if value and (value < 1900 or value > current_year + 5):
        raise ValidationError(f'Year of manufacture must be between 1900 and {current_year + 5}.')

def validate_phone_number(value):
    if value and not re.fullmatch(r'^\d{7,15}$', value):
        raise ValidationError('Phone number must contain only digits and be between 7 and 15 digits long.')

def validate_date_of_birth(value):
    if value and value >= timezone.now().date():
        raise ValidationError('Date of birth cannot be in the future.')

def validate_single_letter_column(value):
    if not value.isalpha() or len(value) > 1:
        raise ValidationError('Column must be a single letter (e.g., A, B).')

def validate_password_length(value):
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
