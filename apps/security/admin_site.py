"""
Custom admin portal for HO-ME.

A self-contained AdminSite with:
- Branded login (dusk palette, username + password)
- Permission gating: Vision 100DM35 (MEL) models only for staff flagged is_mel_admin
- Dashboard with editable sections + submission inboxes
"""

from django.contrib import admin
from django.urls import NoReverseMatch, reverse


class HOMESecurityAdminSite(admin.AdminSite):
    site_header = "HO-ME Admin Portal"
    site_title = "HO-ME Admin"
    index_title = "Content & Operations Hub"
    site_url = "/"
    enable_nav_sidebar = True
    index_template = "admin/index.html"

    def has_permission(self, request):
        """Staff + active only."""
        return request.user.is_active and request.user.is_staff

    # -----------------------------------------------------------------------
    # Professional dashboard: live site status, charts & quick actions
    # -----------------------------------------------------------------------
    def index(self, request, extra_context=None):
        from datetime import timedelta

        from django.db.models import Count, Q
        from django.db.models.functions import TruncDate
        from django.urls import NoReverseMatch, reverse
        from django.utils import timezone

        from apps.accounts.models import (
            ChurchPartnershipApplication,
            PrayerSignup,
            User,
            VolunteerStaffApplication,
        )
        from apps.cms_content.models import ContentTranslation, MelIndicator, RegionHub, Story
        from apps.core.models import ChatbotEntry
        from apps.resources.models import AccessRequest, Resource
        from apps.security.models import AuditLog

        stats = {
            "stories_total": Story.objects.count(),
            "stories_approved": Story.objects.filter(safety_review_status="approved").count(),
            "stories_pending": Story.objects.filter(safety_review_status="pending").count(),
            "stories_blocked": Story.objects.filter(safety_review_status="blocked").count(),
            "resources_total": Resource.objects.count(),
            "resources_published": Resource.objects.filter(published=True).count(),
            "resources_unpublished": Resource.objects.filter(published=False).count(),
            "access_pending": AccessRequest.objects.filter(status="pending").count(),
            "access_total": AccessRequest.objects.count(),
            "prayer_total": PrayerSignup.objects.count(),
            "partnership_total": ChurchPartnershipApplication.objects.count(),
            "volunteer_total": VolunteerStaffApplication.objects.count(),
            "chatbot_active": ChatbotEntry.objects.filter(is_active=True).count(),
            "chatbot_total": ChatbotEntry.objects.count(),
            "translations_total": ContentTranslation.objects.count(),
            "hubs_active": RegionHub.objects.filter(is_active=True).count(),
            "users_total": User.objects.count(),
        }
        stats["submissions_30d"] = sum(
            model.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
            for model in (AccessRequest, PrayerSignup, ChurchPartnershipApplication, VolunteerStaffApplication)
        )

        # ---- audit trail stats ----
        now = timezone.now()
        stats["audit_24h"] = AuditLog.objects.filter(timestamp__gte=now - timedelta(days=1)).count()
        stats["audit_failed_logins_24h"] = AuditLog.objects.filter(
            timestamp__gte=now - timedelta(days=1), action__in=("login_failed", "lockout")
        ).count()
        stats["audit_total"] = AuditLog.objects.count()

        # ---- chart data ----
        story_kinds = {
            row["kind"]: row["c"]
            for row in Story.objects.values("kind").annotate(c=Count("id"))
        }
        story_status = {
            "approved": Story.objects.filter(safety_review_status="approved").count(),
            "pending": Story.objects.filter(safety_review_status="pending").count(),
            "blocked": Story.objects.filter(safety_review_status="blocked").count(),
        }
        access_status = {"pending": 0, "approved": 0, "denied": 0}
        access_status.update({
            row["status"]: row["c"]
            for row in AccessRequest.objects.values("status").annotate(c=Count("id"))
        })

        days = [timezone.localdate() - timedelta(days=i) for i in range(13, -1, -1)]
        series = {}
        for key, model in (
            ("access", AccessRequest),
            ("prayer", PrayerSignup),
            ("partnership", ChurchPartnershipApplication),
            ("volunteer", VolunteerStaffApplication),
        ):
            per_day = {
                row["d"]: row["c"]
                for row in model.objects.filter(created_at__date__gte=days[0])
                .annotate(d=TruncDate("created_at"))
                .values("d")
                .annotate(c=Count("id"))
            }
            series[key] = [per_day.get(day, 0) for day in days]

        resources_by_cat = [
            {
                "name": row["category__name"] or "—",
                "total": row["total"],
                "published": row["pub"],
            }
            for row in Resource.objects.values("category__name")
            .annotate(total=Count("id"), pub=Count("id", filter=Q(published=True)))
            .order_by("-total")[:8]
        ]

        mel_ok = request.user.is_superuser or getattr(request.user, "is_mel_admin", False)
        mel_data = [
            {"code": i.code, "name": i.name, "pct": max(0, min(int(i.progress_pct), 100))}
            for i in MelIndicator.objects.all()[:12]
        ] if mel_ok else []

        charts = {
            "days": [d.strftime("%b %d") for d in days],
            "series": series,
            "story_kinds": story_kinds,
            "story_status": story_status,
            "access_status": access_status,
            "resources_by_cat": resources_by_cat,
            "mel": mel_data,
        }

        # ---- recent submissions inbox (last 8 across the 4 forms) ----
        recent = []
        for type_key, type_label, model, title_field in (
            ("access", "Access request", AccessRequest, lambda o: f"{o.full_name} → {o.resource.title}"),
            ("prayer", "Prayer signup", PrayerSignup, lambda o: o.full_name),
            ("partnership", "Church partnership", ChurchPartnershipApplication, lambda o: o.church_name or o.full_name),
            ("volunteer", "Volunteer application", VolunteerStaffApplication, lambda o: o.full_name),
        ):
            for o in model.objects.order_by("-created_at")[:5]:
                try:
                    url = reverse(
                        f"admin_portal:{o._meta.app_label}_{o._meta.model_name}_change",
                        args=[o.pk],
                    )
                except NoReverseMatch:
                    url = ""
                recent.append({
                    "type": type_label,
                    "title": title_field(o),
                    "status": o.status,
                    "date": timezone.localtime(o.created_at).strftime("%b %d, %H:%M"),
                    "url": url,
                })
        recent.sort(key=lambda x: x["date"], reverse=True)
        recent = recent[:8]

        # ---- recent admin activity (audit trail) ----
        recent_audit = [
            {
                "time": timezone.localtime(a.timestamp).strftime("%b %d, %H:%M"),
                "who": a.username or "—",
                "action": a.action,
                "action_label": a.get_action_display(),
                "repr": (a.object_repr or a.note or "")[:70],
            }
            for a in AuditLog.objects.all()[:8]
        ]

        # ---- quick actions ----
        quick_links = []
        for label, model in (
            ("Site settings", None),
            ("Stories", Story),
            ("Resources", Resource),
            ("Access requests", AccessRequest),
            ("Chatbot Q&A", ChatbotEntry),
            ("Content translations", ContentTranslation),
            ("Region hubs", RegionHub),
            ("MEL indicators", MelIndicator),
        ):
            if model is None:
                model = __import__("apps.core.models", fromlist=["SiteSetting"]).SiteSetting
            try:
                url = reverse(f"admin_portal:{model._meta.app_label}_{model._meta.model_name}_changelist")
            except NoReverseMatch:
                continue
            if label == "MEL indicators" and not mel_ok:
                continue
            quick_links.append((label, url))

        extra_context = dict(extra_context or {})
        extra_context.update({
            "title": self.index_title,
            "subtitle": None,
            "stats": stats,
            "charts": charts,
            "recent": recent,
            "recent_audit": recent_audit,
            "quick_links": quick_links,
            "mel_ok": mel_ok,
            "has_issues": bool(
                stats["stories_pending"] or stats["access_pending"] or stats["stories_blocked"]
            ),
        })
        return super().index(request, extra_context)

    def login(self, request, extra_context=None):
        """Use the HO-ME branded login."""
        from apps.security.views import HOMESecurityLoginView
        return HOMESecurityLoginView.as_view()(request)

    def get_urls(self):
        urls = super().get_urls()
        return urls

    def each_context(self, request):
        ctx = super().each_context(request)
        # Branding for the custom login template
        if request.resolver_match and request.resolver_match.view_name == self.name + ".login":
            ctx["branding"] = True
        # Site logo (same one used on the public website) for the admin chrome
        try:
            from apps.core.models import SiteSetting
            s = SiteSetting.load()
            ctx["site_logo_url"] = s.logo.url if s.logo else ""
            ctx["site_brand_name"] = s.site_name
        except Exception:
            ctx["site_logo_url"] = ""
        return ctx


admin_site = HOMESecurityAdminSite(name="admin_portal")
