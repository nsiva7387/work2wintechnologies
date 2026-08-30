from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Registration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("phone", models.CharField(max_length=25)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("course", models.CharField(blank=True, max_length=120)),
                ("message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
