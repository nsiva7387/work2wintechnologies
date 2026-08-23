from app import validate_enquiry


BASE = {"name": "Asha Kumar", "whatsapp": "+91 6300157088", "email": "asha@example.com", "course": "Python", "message": ""}


def test_missing_name():
    data = BASE | {"name": ""}
    assert "name" in validate_enquiry(data)[1]


def test_email_is_optional_but_must_be_valid_when_provided():
    assert "email" not in validate_enquiry(BASE | {"email": ""})[1]
    assert "email" in validate_enquiry(BASE | {"email": "not-an-email"})[1]


def test_missing_whatsapp():
    assert "whatsapp" in validate_enquiry(BASE | {"whatsapp": "abc"})[1]


def test_missing_or_invalid_course():
    assert "course" in validate_enquiry(BASE | {"course": ""})[1]
    assert "course" in validate_enquiry(BASE | {"course": "Unknown"})[1]
