import re

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            f'Год {value} больше текущего!',
            params={'value': value},
        )


def validate_username(username):
    if not re.match(r'^[\w.@+-]+\Z', username):
        raise ValidationError('Имя пользователя содержит запрещенные символы')
    if username == "me":
        raise serializers.ValidationError(
            {'username': "Username 'me' is not valid"})
