from django.core.exceptions import ValidationError
import re

def validate_username(value):
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        raise ValidationError(
            'Kullanıcı adı sadece alfanümerik karakterlerden oluşabilir',
            code='invalid_username'
        )