import re
from datetime import datetime

from django.core.exceptions import ValidationError

from api_yamdb.settings import USERNAME_REGEX, RESERVED_USERNAMES

MESSAGE_REGEX = 'Enter a valid value. Invalid simbols: {}'
MESSAGE_ME = 'Username "me" is not valid.'
MESSAGE_YEAR = (
    'Указанная дата произведения {value}, '
    'не может быть позже текущего года {year_now}'
)


def regex_validator(value):
    invalid_simbols = ''.join(set(re.sub(USERNAME_REGEX, '', str(value))))
    if invalid_simbols:
        raise ValidationError(MESSAGE_REGEX.format(invalid_simbols))


def me_validator(value):
    for reserved_username in RESERVED_USERNAMES:
        if value == reserved_username:
            raise ValidationError(MESSAGE_ME)


def validate_year_not_in_future(value):
    year_now = datetime.now().year
    if value > year_now:
        raise ValidationError(
            MESSAGE_YEAR.format(value=value, year_now=year_now)
        )
    return value
