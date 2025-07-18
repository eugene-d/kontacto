import re
from datetime import date, datetime
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_phone(phone: str) -> str:
    """
    Validate and normalize phone numbers.

    Returns normalized phone number.
    Args:
        phone: Phone number string to validate

    Returns:
        Normalized phone number

    Raises:
        ValidationError: If phone number is invalid
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r"[^\d+]", "", phone)

    if len(cleaned) == 10 and cleaned.isdigit():
        return cleaned

    raise ValidationError(f"Phone number must be 10 digits long: {phone}")


def validate_email(email: str) -> str:
    """
    Validate email addresses using RFC-compliant regex.

    Args:
        email: Email address to validate

    Returns:
        Normalized email (lowercase)

    Raises:
        ValidationError: If email is invalid
    """
    # RFC-compliant email regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")

    return email.lower()


def validate_birthday(birthday: date) -> date:
    """
    Validate birthday dates.

    Args:
        birthday: Date to validate

    Returns:
        Validated birthday

    Raises:
        ValidationError: If birthday is invalid
    """
    today = date.today()

    # Check if birthday is in the future
    if birthday > today:
        raise ValidationError("Birthday cannot be in the future")

    # Check reasonable age range (0-150 years)
    age = today.year - birthday.year
    if age > 150:
        raise ValidationError("Age cannot exceed 150 years")

    return birthday


def parse_date(date_string: str) -> Optional[date]:
    """
    Parse date string into date object.

    Supports multiple date formats.

    Args:
        date_string: Date string to parse

    Returns:
        Parsed date or None if parsing fails
    """
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue

    return None
