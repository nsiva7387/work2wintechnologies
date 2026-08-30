from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0002_registration")]
    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="photo",
            field=models.ImageField(blank=True, upload_to="student_photos/%Y/%m/"),
        ),
        migrations.AddField(
            model_name="studentprofile",
            name="course_expires_on",
            field=models.DateField(blank=True, help_text="Leave empty if the course has no expiry date.", null=True),
        ),
    ]
