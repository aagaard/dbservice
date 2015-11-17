import re

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
import psycopg2.extensions


def _parse_opt_num(s):
    if not s:
        # For the ISO 8601 duration specifications, fields need not be
        # explicitly included if their value is zero --- None from regexp
        # should become 0.
        return 0
    try:
        # Prefer integers.  Only last specified field is allowed to contain a
        # fractional part, though we don't explicitly check this.
        # TODO: Check; is this still necessary/relevant/preferable to using
        # float() for all fields?
        return int(s)
    except ValueError:
        return float(s.replace(',', '.'))


# PnW
ISO_WEEK_RX = re.compile(
    r'^P(\d+(?:[.,]\d*)?)W$')

# P[nY][nM][nD][T[nH][nM][nS]]
ISO_RX = re.compile(
    r'^P'
    r'(?:(\d+(?:[.,]\d*)?)Y)?'  # year
    r'(?:(\d+(?:[.,]\d*)?)M)?'  # month
    r'(?:(\d+(?:[.,]\d*)?)D)?'  # day
    r'(?:T'  # start optional time part
    r'(?:(\d+(?:[.,]\d*)?)H)?'  # hour
    r'(?:(\d+(?:[.,]\d*)?)M)?'  # minute
    r'(?:(\d+(?:[.,]\d*)?)S)?'  # second
    r')?'  # end optional time part
    r'$')


def _iso8601_to_relativedelta(s):
    """
    Parse a duration specification in the accepted ISO 8601 formats
    'PnYnMnDTnHnMnS' or 'PnW' to a ``relativedelta`` object.
    """
    match = ISO_RX.match(s)
    if match:
        years, months, days, hours, minutes, seconds = \
            [_parse_opt_num(n) for n in match.groups()]
        return relativedelta(
            years=years, months=months, days=days,
            hours=hours, minutes=minutes, seconds=seconds)
    match = ISO_WEEK_RX.match(s)
    if match:
        weeks = _parse_opt_num(match.groups()[0])
        return relativedelta(weeks=weeks)
    raise ValueError('Invalid ISO 8601 duration string %s' % s)


def _relativedelta_to_iso8601(val):
    """
    Construct an ISO 8601 duration specification string from the provided
    ``relativedelta`` object.
    """
    if val.leapdays:
        raise ValueError('"leapdays" not representable')
    if any([getattr(val, f) is not None for f in (
            'year', 'month', 'day', 'weekday',
            'hour', 'minute', 'second', 'microsecond')]):
        raise ValueError(
            'relativedelta {} represents an absoluet timestamp; '
            'not a duration'.format(val))
    seconds = val.seconds
    if val.microseconds:
        seconds += val.microseconds / 1000000.0
    return 'P{years}Y{months}M{days}DT{hours}H{minutes}M{seconds}S'.format(
        years=val.years, months=val.months, days=val.days,
        hours=val.hours, minutes=val.minutes, seconds=seconds)


# [Y year[s]] [M mon[s]] [D day[s]] [HH:MM:SS[.s*]
POSTGRES_RX = re.compile(
    r'^'
    r'(?:(\d+) years? ?)?'
    r'(?:(\d+) mons? ?)?'
    r'(?:(\d+) days? ?)?'
    r'(?:'  # start optional time part
    r'(\d+):(\d+):(\d+(?:\.\d*)?)'
    r')?'  # end optional time part
    r'$')


def _postgres_to_relativedelta(s):
    """
    Parse interval output in the default "postgres" style for PostgreSQL into a
    ``relativedelta``.
    """
    match = POSTGRES_RX.match(s)
    if match:
        years, months, days, hours, minutes, seconds = [
            _parse_opt_num(n) for n in match.groups()]
        return relativedelta(
            years=years, months=months, days=days,
            hours=hours, minutes=minutes, seconds=seconds)
    raise ValueError('Unrecognized postgres interval string \'%s\'' % s)


# Set "output" type for INTERVALs from the DB to be relativedelta.
INTERVAL2RELATIVEDELTA = psycopg2.extensions.new_type(
    psycopg2.extensions.INTERVAL.values,
    'INTERVAL2RELATIVEDELTA',
    lambda value, curs:
    _postgres_to_relativedelta(value) if value is not None else None)
psycopg2.extensions.register_type(INTERVAL2RELATIVEDELTA)


# Set conversion of relativedelta on "input" to the DB to be an appropriate ISO
# 8601 duration string.
def _adapt_relativedelta(val):
    return psycopg2.extensions.AsIs("'{}'".format(
        _relativedelta_to_iso8601(val)))
psycopg2.extensions.register_adapter(relativedelta, _adapt_relativedelta)


class IntervalField(models.Field):
    description = 'A time interval'

    __metaclass__ = models.SubfieldBase

    default_error_messages = {
        'invalid': _("'%s' value has an invalid format.  It must be in "
                     "ISO 8601 duration (PnYnMnDTnHnMnS or PnW) format."),
    }

    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] != \
                'django.db.backends.postgresql_psycopg2':
            raise NotImplementedError('only implemented for PostgreSQL')
        return 'interval'

    def to_python(self, value):
        if isinstance(value, relativedelta):
            return value
        if value is None or value == '':
            return None
        try:
            return _iso8601_to_relativedelta(value)
        except ValueError:
            # any parse error becomes the same "invalid" error...
            msg = self.error_messages['invalid'] % value
            raise ValidationError(msg)

    def get_db_prep_value(self, value, connection, prepared=False):
        if connection.settings_dict['ENGINE'] != \
                'django.db.backends.postgresql_psycopg2':
            raise NotImplementedError('only implemented for PostgreSQL')
        return super().get_db_prep_value(
            value, connection, prepared)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if value is None:
            return ''
        else:
            return _relativedelta_to_iso8601(value)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        [],
        [r'^dbservice\.apps\.utils\.fields\.IntervalField'])
except ImportError:
    pass
