from django.core.exceptions import ValidationError


def validate_all_number(value):
    if not value.isnumeric():
        raise ValidationError('This field must be numeric')