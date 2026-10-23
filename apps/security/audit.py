"""
Audit plumbing for the HO-ME admin portal.

Design:
- A tiny middleware stores the *current request* in thread-local storage, so
  signal receivers can attribute model changes to the staff member (and IP)
  that caused them — even for saves triggered deep inside admin forms.
- Signal receivers record:
    * authentication: sign-in, sign-out, failed sign-in
    * content CRUD:   create/update/delete of every managed content model
- Events fired without a request (migrations, seed scripts) are ignored so the
  log only reflects real usage.
"""

import threading

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AuditLog

_request_ctx = threading.local()


# ---------------------------------------------------------------------------
# Request context (set by apps.security.middleware.AuditRequestMiddleware)
# ---------------------------------------------------------------------------

def set_current_request(request):
    _request_ctx.request = request


def get_current_request():
    return getattr(_request_ctx, "request", None)


def get_client_ip(request):
    """Best-effort client IP (honours the proxy header used in production)."""
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
    return ip or None


def get_user_agent(request):
    if request is None:
        return ""
    return (request.META.get("HTTP_USER_AGENT") or "")[:255]


# ---------------------------------------------------------------------------
# Core recorder
# ---------------------------------------------------------------------------

def record(action, *, user=None, obj=None, note="", request=None, username=""):
    """
    Write one audit entry. Never raises — an audit failure must never break a
    real request.

    Actor resolution order: explicit `user` → current request's staff user →
    "(public)" when an anonymous request caused the event.
    """
    try:
        req = request or get_current_request()
        if user is None and req is not None:
            req_user = getattr(req, "user", None)
            if req_user is not None and req_user.is_authenticated:
                user = req_user

        if user is not None:
            who = username or user.get_username()
        elif username:
            who = username
        elif req is not None:
            who = "(public)"
        else:
            who = ""

        data = {
            "user": user,
            "username": who[:150],
            "action": action,
            "ip_address": get_client_ip(req),
            "user_agent": get_user_agent(req),
            "note": note or "",
        }
        if obj is not None:
            data["object_id"] = str(obj.pk)[:64]
            data["object_repr"] = str(obj)[:255]
            try:
                data["content_type"] = ContentType.objects.get_for_model(obj)
            except Exception:
                pass
        AuditLog.objects.create(**data)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Content model registry — what gets CRUD-audited
# ---------------------------------------------------------------------------

TRACKED_MODELS = None  # built lazily (apps may not be ready at import time)


def _tracked_set():
    global TRACKED_MODELS
    if TRACKED_MODELS is None:
        from apps.accounts.models import (
            ChurchPartnershipApplication,
            GivingOption,
            PrayerSignup,
            VolunteerStaffApplication,
        )
        from apps.cms_content.models import (
            ContentTranslation,
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
            ChatbotEntry,
            CoreValue,
            LeadershipProfile,
            PartnerLogo,
            SiteSetting,
            TimelineMilestone,
        )
        from apps.resources.models import (
            AccessRequest,
            Language,
            Resource,
            ResourceCategory,
            TargetAudience,
        )
        from django.contrib.auth import get_user_model

        TRACKED_MODELS = frozenset({
            # Core site content & settings
            SiteSetting, PartnerLogo, TimelineMilestone, LeadershipProfile, CoreValue,
            ChatbotEntry,
            # What we do / where we work / MEL
            McmsStep, Pillar, DmmGenerationStep, TrainingProgram, KingdomBusinessIga,
            DigitalMinistrySummary, RegionHub, MelIndicator,
            # Impact stories
            Story,
            # Resources & access
            Resource, ResourceCategory, Language, TargetAudience, AccessRequest,
            # Engagement submissions & giving
            PrayerSignup, ChurchPartnershipApplication, VolunteerStaffApplication,
            GivingOption,
            # Staff accounts & translations
            get_user_model(), ContentTranslation,
        })
    return TRACKED_MODELS


# ---------------------------------------------------------------------------
# Signal receivers
# ---------------------------------------------------------------------------

@receiver(post_save, dispatch_uid="home_audit_post_save")
def _audit_post_save(sender, instance, created, **kwargs):
    if sender not in _tracked_set():
        return
    if created:
        try:
            from apps.core.models import SiteSetting
            if sender is SiteSetting:
                return  # lazy singleton bootstrap (SiteSetting.load()), not an admin action
        except Exception:
            pass
    req = get_current_request()
    if req is None:
        return  # migrations / seed scripts — not audited
    record(AuditLog.CREATE if created else AuditLog.UPDATE, obj=instance, request=req)


@receiver(post_delete, dispatch_uid="home_audit_post_delete")
def _audit_post_delete(sender, instance, **kwargs):
    if sender not in _tracked_set():
        return
    req = get_current_request()
    if req is None:
        return
    record(AuditLog.DELETE, obj=instance, request=req)


@receiver(user_logged_in, dispatch_uid="home_audit_login")
def _audit_login(sender, request, user, **kwargs):
    if user is not None and user.is_authenticated:
        record(AuditLog.LOGIN, user=user, request=request)


@receiver(user_logged_out, dispatch_uid="home_audit_logout")
def _audit_logout(sender, request, user, **kwargs):
    if user is not None and user.is_authenticated:
        record(AuditLog.LOGOUT, user=user, request=request)
