from datetime import datetime


def validate_required(value, field_name):
    if value is None or str(value).strip() == '':
        raise ValueError(f'{field_name} is required.')
    return str(value).strip()


def validate_date(value, field_name):
    if value in (None, ''):
        return None
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{field_name} must be a valid date.') from exc
    return value


def safe_decimal(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError('Enter a valid numeric value.')
