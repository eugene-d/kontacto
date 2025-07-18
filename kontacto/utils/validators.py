"""Validators for various data types in the Personal Assistant application."""

import re
from datetime import date, datetime
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_phone(phone: str) -> str:
    """
    Validate and normalize phone numbers.

    Supports international formats and common variations.
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

    # Check various phone patterns
    patterns = [
        r"^\+?1?\d{10}$",  # US numbers with optional +1
        r"^\+\d{1,3}\d{7,14}$",  # International format
        r"^\d{7,15}$",  # Generic format (7-15 digits)
        r"^\d{3}-\d{4}$",  # XXX-XXXX format
        r"^\d{3}-\d{3}-\d{4}$",  # XXX-XXX-XXXX format
    ]

    for pattern in patterns:
        if re.match(pattern, cleaned):
            return cleaned

    raise ValidationError(f"Invalid phone number format: {phone}")


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
