from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/course-registration/", views.public_registration, name="public_registration"),
    path("api/enquiry/", views.public_registration, name="public_enquiry"),
    path("announcements/", views.announcement_list, name="announcement_list"),
    path("announcements/<int:announcement_id>/poster/", views.announcement_poster, name="announcement_poster"),
    path("announcements/<int:announcement_id>/", views.announcement_detail, name="announcement_detail"),
    path("student-feedback/", views.feedback_list, name="feedback_list"),
]
