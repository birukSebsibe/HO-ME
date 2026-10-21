"""
Model registration for the HO-ME admin portal.

All public-facing content is fully editable here without touching code.
Vision 100DM35 (MEL) data is restricted to users flagged is_mel_admin.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html

from apps.core.models import (
    ChatbotEntry,
    CoreValue,
    LeadershipProfile,
    PartnerLogo,
    SiteSetting,
    TimelineMilestone,
)
from apps.cms_content.models import ContentTranslation
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
from apps.resources.models import (
    AccessRequest,
    Language,
    Resource,
    ResourceCategory,
    TargetAudience,
)
from apps.accounts.models import (
    ChurchPartnershipApplication,
    GivingOption,
    PrayerSignup,
    User,
    VolunteerStaffApplication,
)

from .admin_site import admin_site


# ---------------------------------------------------------------------------
# Rich-text editor (no CDN — lightweight contentEditable widget)
# ---------------------------------------------------------------------------

class RichTextFieldFormMixin(forms.ModelForm):
    """Renders listed fields with the .js-rte textarea + loads static/security/rte.js."""

    class Media:
        js = ("security/rte.js",)

    RTE_FIELDS = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.RTE_FIELDS:
            if f in self.fields:
                self.fields[f].widget = forms.Textarea(attrs={"class": "js-rte", "rows": 12})


class StoryAdminForm(RichTextFieldFormMixin):
    class Meta:
        model = Story
        fields = "__all__"

    RTE_FIELDS = ("body",)


# ---------------------------------------------------------------------------
# User = staff accounts + MEL admin gate
# ---------------------------------------------------------------------------

@admin.register(User, site=admin_site)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "full_name", "email", "is_staff", "is_mel_admin", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "is_mel_admin")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "email", "job_title", "phone")}),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_mel_admin", "groups", "user_permissions"),
        }),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")

    def full_name(self, obj):
        return obj.get_full_display_name()


# ---------------------------------------------------------------------------
# Core: global site settings (singleton + related cards/lists)
# ---------------------------------------------------------------------------

class PartnerLogoInline(admin.TabularInline):
    model = PartnerLogo
    extra = 1


class LeadershipInline(admin.StackedInline):
    model = LeadershipProfile
    extra = 1
    fields = ("name", "role", "photo", "bio", "email", "is_active", "order")


class TimelineInline(admin.TabularInline):
    model = TimelineMilestone
    extra = 1
    fields = ("year", "title", "description", "icon", "is_public", "order")


class CoreValuesInline(admin.StackedInline):
    model = CoreValue
    extra = 0
    max_num = 6
    fields = ("number", "title", "body", "icon")


@admin.register(SiteSetting, site=admin_site)
class SiteSettingAdmin(admin.ModelAdmin):
    inlines = (PartnerLogoInline, LeadershipInline, TimelineInline, CoreValuesInline)

    def has_add_permission(self, request):
        # Singleton — one master row only
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ("Identity & branding", {
            "fields": ("site_name", "site_tagline", "logo", "favicon"),
        }),
        ("Hero section", {
            "fields": (
                "hero_variant", "headline_a", "headline_b", "subheadline",
                ("hero_cta_text_1", "hero_cta_url_1"),
                ("hero_cta_text_2", "hero_cta_url_2"),
            ),
        }),
        ("Impact counter strip", {
            "fields": ("counter_churches", "counter_years", "counter_upgs", "counter_hubs", "counter_network"),
        }),
        ("Contact", {
            "fields": ("contact_email", "contact_phone", "contact_address", "contact_map_embed_url"),
        }),
        ("Social links", {
            "fields": ("social_facebook", "social_x", "social_instagram", "social_youtube", "social_linkedin"),
        }),
        ("Footer", {
            "fields": ("privacy_policy_url", "transparency_url", "footer_note"),
        }),
    )


# The timeline also gets a top-level entry for direct management
@admin.register(TimelineMilestone, site=admin_site)
class TimelineMilestoneAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "icon", "is_public", "order")
    list_filter = ("is_public", "year")
    search_fields = ("title", "description")
    list_editable = ("is_public", "order")


# ---------------------------------------------------------------------------
# What We Do
# ---------------------------------------------------------------------------

@admin.register(McmsStep, site=admin_site)
class McmsStepAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "short_line", "order", "is_active")
    ordering = ("order",)
    list_editable = ("order", "is_active")
    prepopulated_fields = {}


@admin.register(Pillar, site=admin_site)
class PillarAdmin(admin.ModelAdmin):
    list_display = ("title", "number", "icon", "is_active")
    ordering = ("number",)


@admin.register(DmmGenerationStep, site=admin_site)
class DmmGenerationStepAdmin(admin.ModelAdmin):
    list_display = ("title", "number", "icon")
    ordering = ("number",)


@admin.register(TrainingProgram, site=admin_site)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "duration", "is_active")
    search_fields = ("name", "overview")
    list_editable = ("is_active",)


@admin.register(KingdomBusinessIga, site=admin_site)
class KingdomBusinessIgaAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    ordering = ("order",)
    list_editable = ("order", "is_active")


@admin.register(DigitalMinistrySummary, site=admin_site)
class DigitalMinistrySummaryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not DigitalMinistrySummary.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Where We Work
# ---------------------------------------------------------------------------

@admin.register(RegionHub, site=admin_site)
class RegionHubAdmin(admin.ModelAdmin):
    list_display = ("name", "region_type", "upg_count", "status", "total_churches", "is_active")
    list_filter = ("region_type", "status", "is_active")
    list_editable = ("upg_count", "status", "is_active")
    search_fields = ("name", "summary")


# ---------------------------------------------------------------------------
# Vision 100DM35 — MEL indicator tracker (restricted)
# ---------------------------------------------------------------------------

@admin.register(MelIndicator, site=admin_site)
class MelIndicatorAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "baseline_2025", "current_value", "target_2030", "progress_preview")
    search_fields = ("code", "name", "pillar")
    list_filter = ("pillar",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if getattr(request.user, "is_mel_admin", False) or request.user.is_superuser:
            return qs
        return qs.none()

    def progress_preview(self, obj):
        pct = obj.progress_pct
        color = "md-green" if pct >= 50 else ("md-yellow" if pct >= 25 else "md-red")
        return format_html('<b>{}%</b>', pct)

    progress_preview.short_description = "Progress to 2030"

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or getattr(request.user, "is_mel_admin", False)

    has_change_permission = has_view_permission
    has_add_permission = has_view_permission
    has_module_permission = has_view_permission
    has_delete_permission = has_view_permission


# ---------------------------------------------------------------------------
# Impact & Stories
# ---------------------------------------------------------------------------

@admin.register(Story, site=admin_site)
class StoryAdmin(admin.ModelAdmin):
    form = StoryAdminForm
    list_display = ("title", "kind", "region", "safety_review_status", "published_at", "is_featured")
    list_filter = ("kind", "region", "safety_review_status", "is_featured")
    search_fields = ("title", "excerpt", "body", "region_tags", "tags")
    date_hierarchy = "published_at"
    list_editable = ("safety_review_status", "is_featured")
    readonly_fields = ("slug", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("kind", "title", "slug", "excerpt", "body")}),
        ("Media & region", {"fields": ("cover_image", "video_url", "region", "region_tags", "tags")}),
        ("Publishing & safety review", {
            "fields": ("safety_review_status", "published_at", "is_featured")
        }),
        ("Timestamps (auto)", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@admin.register(ResourceCategory, site=admin_site)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Language, site=admin_site)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code")


@admin.register(TargetAudience, site=admin_site)
class TargetAudienceAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Resource, site=admin_site)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "language", "visibility", "view_count", "download_count", "published")
    list_filter = ("category", "language", "visibility", "published", "audiences")
    search_fields = ("title", "description")
    list_editable = ("visibility", "published")
    readonly_fields = ("view_count", "download_count", "uuid", "slug", "created_at", "updated_at")
    filter_horizontal = ("audiences",)


@admin.register(AccessRequest, site=admin_site)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "resource", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("full_name", "email", "resource__title")
    list_editable = ("status",)


# ---------------------------------------------------------------------------
# Engagement submissions
# ---------------------------------------------------------------------------

@admin.register(PrayerSignup, site=admin_site)
class PrayerSignupAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "frequency", "region_hub", "status", "created_at")
    list_filter = ("frequency", "status")
    search_fields = ("full_name", "email", "topics_of_interest")


@admin.register(ChurchPartnershipApplication, site=admin_site)
class ChurchPartnershipAdmin(admin.ModelAdmin):
    list_display = ("church_name", "full_name", "email", "partnership_interest", "status", "created_at")
    list_filter = ("partnership_interest", "status")
    search_fields = ("church_name", "full_name", "email")


@admin.register(VolunteerStaffApplication, site=admin_site)
class VolunteerStaffAdmin(admin.ModelAdmin):
    list_display = ("full_name", "kind", "skills", "region_hub", "status", "created_at")
    list_filter = ("kind", "status")
    search_fields = ("full_name", "email", "skills")


@admin.register(GivingOption, site=admin_site)
class GivingOptionAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "order", "is_active")
    list_editable = ("order", "is_active")


# ---------------------------------------------------------------------------
# Floating chatbot Q&A — manageable pre-defined questions & answers
# ---------------------------------------------------------------------------

@admin.register(ChatbotEntry, site=admin_site)
class ChatbotEntryAdmin(admin.ModelAdmin):
    """'Chatbot Q&A' section in the admin portal sidebar."""

    list_display = ("question", "answer_preview", "keywords", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "answer", "keywords")
    fieldsets = (
        ("Question & answer", {
            "fields": ("question", "answer"),
            "description": (
                "Shown as a clickable chip in the floating chat helper. "
                "The first 6 active entries appear as quick questions."
            ),
        }),
        (None, {"fields": ("keywords", "order", "is_active")}),
    )

    @admin.display(description="Answer")
    def answer_preview(self, obj):
        return (obj.answer[:80] + "…") if len(obj.answer) > 80 else obj.answer


# ---------------------------------------------------------------------------
# Content Translations — per-language overrides of CMS text fields
# ---------------------------------------------------------------------------

@admin.register(ContentTranslation, site=admin_site)
class ContentTranslationAdmin(admin.ModelAdmin):
    """'Content Translations' section: translate any CMS text field into Amharic/Oromifa."""

    list_display = ("content_preview", "field_name", "language", "text_preview", "updated_at")
    list_filter = ("language", "content_type")
    search_fields = ("text", "field_name")
    fields = ("content_type", "object_id", "field_name", "language", "text")

    @admin.display(description="Object")
    def content_preview(self, obj):
        return str(obj.content_object)

    @admin.display(description="Translation")
    def text_preview(self, obj):
        return (obj.text[:80] + "…") if len(obj.text) > 80 else obj.text
