from django.contrib import admin
from .models import Announcement, Course, Registration, StudentFeedback


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "duration", "published", "active", "archived", "updated_at")
    list_filter = ("published", "active", "archived")
    search_fields = ("name", "description")
    actions = ("publish_courses", "unpublish_courses")
    @admin.action(description="Publish selected courses")
    def publish_courses(self, request, queryset): queryset.update(published=True, archived=False)
    @admin.action(description="Unpublish selected courses")
    def unpublish_courses(self, request, queryset): queryset.update(published=False)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "active", "has_whatsapp_group", "publish_from", "publish_until")
    list_filter = ("active", "course")
    search_fields = ("title", "message")

    @admin.display(boolean=True, description="WhatsApp group")
    def has_whatsapp_group(self, obj):
        return bool(obj.whatsapp_group_url)


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "approved", "created_at")
    list_filter = ("approved", "course")
    search_fields = ("name", "message")
    actions = ("approve_feedback", "hide_feedback")
    @admin.action(description="Approve selected feedback")
    def approve_feedback(self, request, queryset): queryset.update(approved=True)
    @admin.action(description="Hide selected feedback")
    def hide_feedback(self, request, queryset): queryset.update(approved=False)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "whatsapp", "email", "course", "status", "created_at")
    list_filter = ("status", "course", "created_at")
    search_fields = ("name", "phone", "whatsapp", "email", "course")
    readonly_fields = ("created_at", "updated_at")
