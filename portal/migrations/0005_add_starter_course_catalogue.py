from django.db import migrations


COURSES = [
    ("Data Analyst", "Learn Excel, SQL, Power BI and practical data analysis for business reporting.", "4 months"),
    ("Data Science", "Build data science foundations using Python, statistics and machine learning concepts.", "6 months"),
    ("Python Programming", "Learn Python from fundamentals to real-world programming projects.", "3 months"),
    ("Python Full Stack", "Build complete web applications with Python, Django, HTML, CSS and JavaScript.", "6 months"),
    ("Java Programming", "Develop strong Java programming skills with object-oriented concepts and projects.", "3 months"),
    ("Java Full Stack", "Learn Java, web development, databases and full-stack application development.", "6 months"),
    ("MySQL", "Design databases and write SQL queries for practical applications.", "2 months"),
    ("Excel & Power BI", "Create advanced spreadsheets, reports, dashboards and business insights.", "3 months"),
    ("HTML, CSS & JavaScript", "Create responsive, interactive websites from the ground up.", "3 months"),
    ("React JS", "Build modern component-based user interfaces with React.", "3 months"),
]


def add_courses(apps, schema_editor):
    Course = apps.get_model("portal", "Course")
    for name, description, duration in COURSES:
        Course.objects.get_or_create(
            name=name,
            defaults={"description": description, "duration": duration, "active": True, "published": True},
        )


class Migration(migrations.Migration):
    dependencies = [("portal", "0004_announcement_publish_from_announcement_publish_until_and_more")]

    operations = [migrations.RunPython(add_courses, migrations.RunPython.noop)]
