import app as app_module


VALID_ENQUIRY = {"name": "Asha Kumar", "whatsapp": "+91 6300157088", "email": "asha@example.com", "course": "Python", "message": "Please share details."}


def make_client(saver=lambda data, url: None):
    app = app_module.create_app({"TESTING": True, "DATABASE_URL": "postgresql://test", "ENQUIRY_SAVER": saver})
    return app.test_client()


def test_home_page_loads_and_lists_courses():
    response = make_client().get("/")
    assert response.status_code == 200
    assert b"Work2Win Technologies" in response.data
    assert b"Python Full Stack" in response.data


def test_api_accepts_valid_enquiry():
    stored = []
    response = make_client(lambda data, url: stored.append(data)).post("/api/enquiry", json=VALID_ENQUIRY)
    assert response.status_code == 201
    assert response.json["success"] is True
    assert stored[0]["course"] == "Python"


def test_database_failure_is_safe():
    def fail(*_): raise RuntimeError("connection problem")
    response = make_client(fail).post("/api/enquiry", json=VALID_ENQUIRY)
    assert response.status_code == 500
    assert b"connection problem" not in response.data


def test_email_failure_does_not_lose_enquiry(monkeypatch):
    stored = []
    monkeypatch.setattr(app_module, "send_email", lambda *_: False)
    app = app_module.create_app({"TESTING": True, "DATABASE_URL": "postgresql://test", "RESEND_API_KEY": "test", "ENQUIRY_SAVER": lambda data, url: stored.append(data)})
    response = app.test_client().post("/api/enquiry", json=VALID_ENQUIRY)
    assert response.status_code == 201
    assert stored
    assert b"still be in touch" in response.data
