"""
Public site views for HO-ME (all pages read CMS models so the portal is fully editable).
"""

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.models import (
    ChurchPartnershipApplication,
    GivingOption,
    PrayerSignup,
    VolunteerStaffApplication,
)
from apps.cms_content.models import (
    DmmGenerationStep,
    DigitalMinistrySummary,
    KingdomBusinessIga,
    McmsStep,
    MelIndicator,
    Pillar,
    RegionHub,
    Story,
    TrainingProgram,
)
from apps.core.models import (
    CoreValue,
    LeadershipProfile,
    SiteSetting,
    TimelineMilestone,
)
from apps.resources.models import (
    AccessRequest,
    Resource,
    ResourceCategory,
    TargetAudience,
)


def _ctx(**extra):
    ctx = {
        "site": SiteSetting.load(),
        "regions": RegionHub.objects.filter(is_active=True),
        "mcms_steps": McmsStep.objects.filter(is_active=True),
        "pillars": Pillar.objects.filter(is_active=True),
    }
    ctx.update(extra)
    return ctx


def home(request):
    s = SiteSetting.load()
    return render(request, "core/home.html", _ctx(
        featured_stories=Story.objects.filter(
            safety_review_status="approved", is_featured=True
        )[:3],
        latest_stories=Story.objects.filter(safety_review_status="approved")[:6],
        partners=s.partner_logos.all(),
    ))


def about(request):
    return render(request, "core/about.html", _ctx(
        milestones=TimelineMilestone.objects.filter(is_public=True).order_by("year", "order"),
        leaders=LeadershipProfile.objects.filter(is_active=True),
        values=CoreValue.objects.all(),
    ))


def what_we_do(request):
    return render(request, "core/what_we_do.html", _ctx(
        dmm_steps=DmmGenerationStep.objects.all(),
        programs=TrainingProgram.objects.filter(is_active=True),
        igas=KingdomBusinessIga.objects.filter(is_active=True),
        digital=DigitalMinistrySummary.load(),
    ))


def where_we_work(request):
    return render(request, "core/where_we_work.html", _ctx())


def vision(request):
    indicators = MelIndicator.objects.all()
    if request.user.is_authenticated and request.user.is_staff and not (
        request.user.is_superuser or request.user.is_mel_admin
    ):
        indicators = MelIndicator.objects.none()
    return render(request, "core/vision.html", _ctx(
        indicators=indicators,
        by_pillar={},
    ))


def impact(request):
    stories = list(Story.objects.filter(safety_review_status="approved"))
    kind = request.GET.get("kind")
    region_q = request.GET.get("region")
    if kind in ("news", "story", "testimony"):
        stories = [s for s in stories if s.kind == kind]
    if region_q:
        stories = [s for s in stories if (s.region and s.region.name == region_q) or (s.region_tags and region_q.lower() in s.region_tags.lower())]
    import json as _json
    stories_json = _json.dumps([
        {
            "title": s.title,
            "excerpt": s.excerpt,
            "kind": s.get_kind_display(),
            "region": s.region.name if s.region else "",
            "slug": s.slug,
            "cover": s.cover_image.url if s.cover_image else "",
        }
        for s in stories
    ])
    return render(request, "core/impact.html", _ctx(
        stories=stories,
        stories_json=stories_json,
        current_kind=kind,
        current_region=region_q,
    ))


def story_detail(request, slug):
    story = get_object_or_404(
        Story, slug=slug, safety_review_status="approved"
    )
    return render(request, "core/story_detail.html", _ctx(story=story, s=SiteSetting.load()))


def library(request):
    qs = Resource.objects.filter(published=True).exclude(visibility="staff")
    categories = ResourceCategory.objects.all()
    languages = list({r.language for r in qs if r.language})
    audiences_qs = TargetAudience.objects.filter(resources__in=qs).distinct()
    import json as _json
    def _is_public(r):
        return r.is_public or (
            r.visibility == "request"
            and request.user.is_authenticated
            and AccessRequest.objects.filter(resource=r, email=request.user.email, status="approved").exists()
        )
    resources_json = _json.dumps([
        {
            "title": r.title,
            "description": r.description,
            "category": r.category.name,
            "language": r.language.name if r.language else "",
            "audiences": [a.name for a in r.audiences.all()],
            "slug": r.slug,
            "is_public": _is_public(r),
            "downloads": r.download_count,
        }
        for r in qs
    ])
    return render(request, "core/library.html", _ctx(
        categories=categories,
        languages=languages,
        audiences=audiences_qs,
        resources_json=resources_json,
    ))


def request_access(request, slug):
    resource = get_object_or_404(Resource, slug=slug, published=True)
    if request.method == "POST":
        AccessRequest.objects.create(
            resource=resource,
            full_name=request.POST.get("full_name", ""),
            email=request.POST.get("email", ""),
            organization=request.POST.get("organization", ""),
            reason=request.POST.get("reason", ""),
        )
        messages.success(request, _("Access request submitted — we'll follow up by email."))
        return redirect("library")
    return render(request, "core/request_access.html", _ctx(resource=resource))


def resource_download(request, slug):
    resource = get_object_or_404(Resource, slug=slug, published=True)
    if not resource.is_public:
        # must be approved-access or staff
        allowed = request.user.is_authenticated and (
            request.user.is_staff or AccessRequest.objects.filter(
                resource=resource, email=request.user.email, status="approved"
            ).exists()
        )
        if not allowed:
            raise PermissionDenied
    resource.download_count += 1
    resource.save(update_fields=["download_count"])
    if resource.file:
        response = redirect(resource.file.url)
    else:
        response = redirect(resource.external_url or "library")
    return response


def privacy(request):
    return render(request, "core/privacy.html", _ctx())


def transparency(request):
    return render(request, "core/transparency.html", _ctx())


def get_involved(request):
    return render(request, "core/get_involved.html", _ctx(
        giving_options=GivingOption.objects.filter(is_active=True),
    ))


# ---------------------------------------------------------------------------
# Interactive public form handlers
# ---------------------------------------------------------------------------

@require_POST
def prayer_signup(request):
    PrayerSignup.objects.create(
        full_name=request.POST.get("full_name", ""),
        email=request.POST.get("email", ""),
        phone=request.POST.get("phone", ""),
        region_hub=request.POST.get("region_hub", ""),
        message=request.POST.get("message", ""),
        frequency=request.POST.get("frequency", "weekly"),
        topics_of_interest=request.POST.get("topics_of_interest", ""),
    )
    if request.headers.get("HX-Request") or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "message": _("Thank you — you've joined the prayer network!")})
    messages.success(request, _("Thank you — you've joined the prayer network!"))
    return redirect("get-involved")


@require_POST
def partnership(request):
    ChurchPartnershipApplication.objects.create(
        full_name=request.POST.get("full_name", ""),
        email=request.POST.get("email", ""),
        phone=request.POST.get("phone", ""),
        region_hub=request.POST.get("region_hub", ""),
        message=request.POST.get("message", ""),
        church_name=request.POST.get("church_name", ""),
        denomination=request.POST.get("denomination", ""),
        city=request.POST.get("city", ""),
        partnership_interest=request.POST.get("partnership_interest", "prayer"),
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "message": _("Application received — our partnerships team will be in touch.")})
    messages.success(request, _("Application received — our partnerships team will be in touch."))
    return redirect("get-involved")


@require_POST
def volunteer(request):
    VolunteerStaffApplication.objects.create(
        full_name=request.POST.get("full_name", ""),
        email=request.POST.get("email", ""),
        phone=request.POST.get("phone", ""),
        region_hub=request.POST.get("region_hub", ""),
        message=request.POST.get("message", ""),
        kind=request.POST.get("kind", "volunteer"),
        skills=request.POST.get("skills", ""),
        availability=request.POST.get("availability", ""),
        references=request.POST.get("references", ""),
        cv_url=request.POST.get("cv_url", ""),
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "message": _("Application received — thank you for offering to serve!")})
    messages.success(request, _("Application received — thank you for offering to serve!"))
    return redirect("get-involved")


def robots(request):
    from django.http import HttpResponse
    return HttpResponse("User-agent: *\nDisallow: /" + settings.ADMIN_URL, content_type="text/plain")


def health(request):
    return JsonResponse({"status": "ok"})
