from django.test import TestCase
from django.urls import reverse

from .models import Course, Registration


class PublicSiteTests(TestCase):
    def setUp(self):
        self.course, _ = Course.objects.get_or_create(name="Python Full Stack", defaults={"published": True})
        if not self.course.published:
            self.course.published = True
            self.course.save(update_fields=("published",))

    def test_homepage_has_no_student_portal_link(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Python Full Stack")
        self.assertNotContains(response, "Student Portal")

    def test_student_portal_urls_are_not_available(self):
        self.assertEqual(self.client.get("/student/").status_code, 404)
        self.assertEqual(self.client.get("/student/login/").status_code, 404)


class RegistrationTests(TestCase):
    def test_public_registration_uses_pending_status(self):
        response = self.client.post(
            reverse("public_registration"),
            data='{"name":"Asha Kumar","whatsapp":"+916300157088","email":"asha@example.com","course":"Python","message":"Please share details."}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        registration = Registration.objects.get()
        self.assertEqual(registration.status, Registration.Status.NEW)
        self.assertEqual(registration.phone, "+916300157088")
