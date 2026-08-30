import json
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Announcement, Course, Registration, StudentFeedback

def home(request):
    now = timezone.now()
    latest_review = StudentFeedback.objects.filter(approved=True).exclude(video_file="").select_related("course").first()
    return render(request, "index.html", {"courses": Course.objects.filter(active=True, published=True, archived=False), "announcement": Announcement.objects.filter(active=True, publish_from__lte=now).filter(Q(publish_until__isnull=True) | Q(publish_until__gte=now)).first(), "latest_review": latest_review})


def announcement_list(request):
    now = timezone.now()
    posts = Announcement.objects.filter(active=True, publish_from__lte=now).filter(Q(publish_until__isnull=True) | Q(publish_until__gte=now))
    return render(request, "announcements/list.html", {"posts": posts})


def announcement_detail(request, announcement_id):
    now = timezone.now()
    post = get_object_or_404(Announcement.objects.filter(active=True, publish_from__lte=now).filter(Q(publish_until__isnull=True) | Q(publish_until__gte=now)), pk=announcement_id)
    return render(request, "announcements/detail.html", {"post": post})


def announcement_poster(request, announcement_id):
    post = get_object_or_404(Announcement, pk=announcement_id, active=True)
    if not post.poster:
        raise Http404
    return FileResponse(post.poster.open("rb"))


def feedback_list(request):
    reviews = StudentFeedback.objects.filter(approved=True).select_related("course")
    return render(request, "feedback/list.html", {"reviews": reviews})

@csrf_exempt
def public_registration(request):
    if request.method != "POST": return JsonResponse({"success": False, "message": "POST required."}, status=405)
    try: data = json.loads(request.body)
    except (TypeError, ValueError): return JsonResponse({"success": False, "message": "Please send valid details."}, status=400)
    clean = {key: str(data.get(key, "")).strip() for key in ("name", "phone", "whatsapp", "email", "course", "message")}
    clean["phone"] = clean["phone"] or clean["whatsapp"]
    errors = {}
    if len(clean["name"]) < 2: errors["name"] = "Enter your full name."
    if len(clean["phone"]) < 7 or len(clean["phone"]) > 25: errors["phone"] = "Enter a valid mobile number."
    if clean["whatsapp"] and (len(clean["whatsapp"]) < 7 or len(clean["whatsapp"]) > 25): errors["whatsapp"] = "Enter a valid WhatsApp number."
    if clean["email"]:
        try: validate_email(clean["email"])
        except ValidationError: errors["email"] = "Enter a valid email address."
    if len(clean["message"]) > 1000: errors["message"] = "Description must be 1,000 characters or fewer."
    if errors: return JsonResponse({"success": False, "message": "Please correct the highlighted fields.", "errors": errors}, status=400)
    duplicate = Registration.objects.filter(name__iexact=clean["name"], phone=clean["phone"], course=clean["course"], status=Registration.Status.NEW).exists()
    if duplicate: return JsonResponse({"success": True, "message": "We already received your registration and will contact you shortly."})
    Registration.objects.create(**clean)
    return JsonResponse({"success": True, "message": "Thanks! Your registration has been received."}, status=201)
