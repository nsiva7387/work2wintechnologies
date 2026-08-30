from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils import timezone

phone_validator = RegexValidator(r"^[+()\-\s0-9]{7,25}$", "Enter a valid phone number.")


class Course(models.Model):
    name = models.CharField("title", max_length=120, unique=True)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Legacy availability setting.")
    published = models.BooleanField(default=False, help_text="Show this course on the public website.")
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name


class Announcement(models.Model):
    course = models.ForeignKey(Course, blank=True, null=True, on_delete=models.CASCADE, related_name="announcements", help_text="Leave empty for every student.")
    title = models.CharField(max_length=180)
    message = models.TextField()
    whatsapp_group_url = models.URLField(
        "WhatsApp group link",
        blank=True,
        help_text="Optional. Leave blank or clear it when the course group is no longer active.",
    )
    poster = models.ImageField(upload_to="posters/%Y/%m/", blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    publish_from = models.DateTimeField(default=timezone.now)
    publish_until = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta: ordering = ["-published_at"]
    def __str__(self): return self.title


class StudentFeedback(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="feedback")
    message = models.TextField(blank=True)
    video_file = models.FileField(
        "student video",
        upload_to="student_feedback_videos/%Y/%m/",
        max_length=255,
        blank=True,
        validators=[FileExtensionValidator(["mp4", "webm", "ogg"])],
        help_text="Upload an MP4, WebM, or OGG video.",
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"{self.name} — {self.course}"


class Registration(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New / Pending"
        CONTACTED = "contacted", "Contacted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    name = models.CharField("full name", max_length=100)
    phone = models.CharField("mobile number", max_length=25, validators=[phone_validator])
    whatsapp = models.CharField("WhatsApp number", max_length=25, blank=True, validators=[phone_validator])
    email = models.EmailField(blank=True)
    course = models.CharField(max_length=120, blank=True)
    message = models.TextField("description / question", blank=True, max_length=1000)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"{self.name} — {self.course or 'General enquiry'}"
