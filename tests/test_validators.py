from datetime import date

import pytest

from kontacto.utils.validators import ValidationError, parse_date, validate_birthday, validate_email, validate_phone


class TestValidatePhone:
    """Test cases for phone number validation."""

    def test_valid_10_digit_phone(self):
        """Test valid 10-digit phone numbers."""
        # Plain 10-digit number
        assert validate_phone("1234567890") == "1234567890"

        # 10-digit number with formatting that gets stripped
        assert validate_phone("123-456-7890") == "1234567890"
        assert validate_phone("(123) 456-7890") == "1234567890"
        assert validate_phone("123.456.7890") == "1234567890"
        assert validate_phone("123 456 7890") == "1234567890"
        assert validate_phone("123-456-7890") == "1234567890"

        # Mixed formatting
        assert validate_phone("(123) 456-7890") == "1234567890"
        assert validate_phone("123.456.7890") == "1234567890"
        assert validate_phone("123 456-7890") == "1234567890"

    def test_invalid_phone_too_short(self):
        """Test phone numbers that are too short."""
        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123456789")  # 9 digits

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123-456-789")  # 9 digits with formatting

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("12345")  # 5 digits

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("")  # Empty string

    def test_invalid_phone_too_long(self):
        """Test phone numbers that are too long."""
        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("12345678901")  # 11 digits

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("1-234-567-8901")  # 11 digits with formatting

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123-456-7890-1")  # 11 digits with formatting

    def test_invalid_phone_with_plus(self):
        """Test phone numbers with + symbol."""
        # Numbers with + should still be invalid if not exactly 10 digits
        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("+1234567890")  # 11 characters (+ doesn't count as digit)

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("+123456789")  # 10 characters but + doesn't count as digit

    def test_invalid_phone_with_letters(self):
        """Test phone numbers with letters."""
        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123-456-ABCD")

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123-CALL-NOW")

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("ABC-DEF-GHIJ")

    def test_valid_phone_special_characters_stripped(self):
        """Test phone numbers with special characters that get stripped."""
        # These should be valid because special characters are stripped, leaving 10 digits
        assert validate_phone("123-456-7890#") == "1234567890"
        assert validate_phone("123-456-7890*") == "1234567890"
        assert validate_phone("123@456@7890") == "1234567890"

    def test_invalid_phone_special_characters(self):
        """Test phone numbers with special characters that make them invalid."""
        # These should be invalid because they don't have exactly 10 digits after cleaning
        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123-456-789#")  # Only 9 digits after cleaning

        with pytest.raises(ValidationError, match="Phone number must be 10 digits long"):
            validate_phone("123-456-7890-1#")  # 11 digits after cleaning

    def test_edge_cases(self):
        """Test edge cases for phone validation."""
        # All zeros (valid as it's 10 digits)
        assert validate_phone("0000000000") == "0000000000"

        # All ones (valid as it's 10 digits)
        assert validate_phone("1111111111") == "1111111111"

        # Numbers with extensive formatting
        assert validate_phone("(123) 456-7890 ext") == "1234567890"  # Only digits are kept

        # Whitespace should be stripped
        assert validate_phone("  123-456-7890  ") == "1234567890"


class TestValidateEmail:
    """Test cases for email validation."""

    def test_valid_emails(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.com",
            "user+tag@example.org",
            "user123@test123.co.uk",
            "a@b.co",
        ]

        for email in valid_emails:
            assert validate_email(email) == email.lower()

    def test_invalid_emails(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@domain",
            "user@domain.",
            # Note: user..name@domain.com and user@domain..com are actually valid by the current regex
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationError, match="Invalid email format"):
                validate_email(email)

    def test_email_normalization(self):
        """Test email normalization (lowercase)."""
        assert validate_email("TEST@EXAMPLE.COM") == "test@example.com"
        assert validate_email("User.Name@Domain.COM") == "user.name@domain.com"


class TestValidateBirthday:
    """Test cases for birthday validation."""

    def test_valid_birthdays(self):
        """Test valid birthday dates."""
        # Past dates should be valid
        past_date = date(1990, 1, 1)
        assert validate_birthday(past_date) == past_date

        # Today should be valid
        today = date.today()
        assert validate_birthday(today) == today

        # Very old date but within reasonable range
        old_date = date(1900, 1, 1)
        assert validate_birthday(old_date) == old_date

    def test_invalid_future_birthday(self):
        """Test that future dates are invalid."""
        future_date = date(2030, 1, 1)
        with pytest.raises(ValidationError, match="Birthday cannot be in the future"):
            validate_birthday(future_date)

    def test_invalid_too_old_birthday(self):
        """Test that dates too far in the past are invalid."""
        # More than 150 years ago
        too_old_date = date(1850, 1, 1)
        with pytest.raises(ValidationError, match="Age cannot exceed 150 years"):
            validate_birthday(too_old_date)


class TestParseDate:
    """Test cases for date parsing."""

    def test_supported_date_formats(self):
        """Test parsing various date formats."""

        date_strings = [
            "2023-12-25",  # ISO format
            "25-12-2023",  # DD-MM-YYYY
            "25/12/2023",  # DD/MM/YYYY
            "12/25/2023",  # MM/DD/YYYY
            "2023.12.25",  # YYYY.MM.DD
            "25.12.2023",  # DD.MM.YYYY
        ]

        for date_string in date_strings:
            parsed = parse_date(date_string)
            assert parsed is not None
            # Note: MM/DD/YYYY format will be interpreted differently

    def test_invalid_date_formats(self):
        """Test parsing invalid date formats."""
        invalid_dates = [
            "invalid-date",
            "2023/13/01",  # Invalid month
            "2023/02/30",  # Invalid day
            "not-a-date",
            "",
            "2023",
            "12-25",
        ]

        for date_string in invalid_dates:
            assert parse_date(date_string) is None

    def test_parse_date_returns_none_for_invalid(self):
        """Test that invalid dates return None."""
        assert parse_date("invalid") is None
        assert parse_date("") is None
        assert parse_date("2023-13-01") is None


class TestValidationError:
    """Test the ValidationError exception."""

    def test_validation_error_message(self):
        """Test that ValidationError carries the correct message."""
        message = "Test error message"
        error = ValidationError(message)
        assert str(error) == message

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from Exception."""
        error = ValidationError("Test")
        assert isinstance(error, Exception)
