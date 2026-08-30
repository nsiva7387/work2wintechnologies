# Generated manually for the initial Work2Win student portal schema.
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Course", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=120, unique=True)), ("description", models.TextField(blank=True)),
            ("active", models.BooleanField(default=True)),
        ], options={"ordering": ["name"]}),
        migrations.CreateModel(name="StudentProfile", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("phone", models.CharField(blank=True, max_length=25)), ("enrolled_on", models.DateField(auto_now_add=True)),
            ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="students", to="portal.course")),
            ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="student_profile", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="StudentFeedback", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100)), ("message", models.TextField(blank=True)), ("video_url", models.URLField(blank=True)),
            ("approved", models.BooleanField(default=False)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("course", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="feedback", to="portal.course")),
            ("student", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="feedback", to="portal.studentprofile")),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="CourseMaterial", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)),
            ("pdf_file", models.FileField(upload_to="materials/%Y/%m/", validators=[django.core.validators.FileExtensionValidator(["pdf"])])),
            ("description", models.TextField(blank=True)), ("uploaded_at", models.DateTimeField(auto_now_add=True)),
            ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="materials", to="portal.course")),
        ], options={"ordering": ["-uploaded_at"]}),
        migrations.CreateModel(name="ClassRecording", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)), ("video_url", models.URLField(help_text="Paste the Google Drive, YouTube, or other recording link.")),
            ("recorded_on", models.DateField()), ("notes", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recordings", to="portal.course")),
        ], options={"ordering": ["-recorded_on", "-created_at"]}),
        migrations.CreateModel(name="Announcement", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)), ("message", models.TextField()), ("poster", models.ImageField(blank=True, upload_to="posters/%Y/%m/")),
            ("published_at", models.DateTimeField(auto_now_add=True)), ("active", models.BooleanField(default=True)),
            ("course", models.ForeignKey(blank=True, help_text="Leave empty to show all students.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="announcements", to="portal.course")),
        ], options={"ordering": ["-published_at"]}),
    ]
