from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

# Re-use the singleton pattern from core
from apps.core.models import SingletonModel


# ---------------------------------------------------------------------------
# What We Do — MCMS cycle, pillars, DMM generations, HOST, IGAs, digital
# ---------------------------------------------------------------------------

class McmsStep(models.Model):
    """One of the four MCMS cycle steps: Mobilize, Catalyze, Multiply, Sustain."""

    key = models.CharField(max_length=20, unique=True)  # mobilize | catalyze | multiply | sustain
    name = models.CharField(max_length=60)
    icon = models.CharField(max_length=40, blank=True, help_text="Lucide icon name.")
    short_line = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"MCMS — {self.name}"


class Pillar(models.Model):
    """One of the 4 ministry pillars."""

    number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=150)
    summary = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("number",)

    def __str__(self):
        return f"Pillar {self.number}: {self.title}"


class DmmGenerationStep(models.Model):
    """A step in the DMM 4-generation multiplication process."""

    number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ("number",)

    def __str__(self):
        return f"Generation {self.number}: {self.title}"


class TrainingProgram(models.Model):
    """HOST school (and similar) overview + fee structures."""

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    kind = models.CharField(max_length=40, blank=True, default="HOST School")
    overview = models.TextField(blank=True)
    duration = models.CharField(max_length=80, blank=True)
    fees = models.TextField(blank=True, help_text="Free text; one fee line per payer/category.")
    fee_rows = models.JSONField(default=list, blank=True, help_text='Optional structured fees, e.g. [{"label":"National tuition","amount":"ETB 12,000"}]')
    icon = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class KingdomBusinessIga(models.Model):
    """Kingdom-business income-generating activities."""

    title = models.CharField(max_length=150)
    summary = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)
    image = models.ImageField(upload_to="iga/", blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order",)
        verbose_name = "Kingdom Business IGA"
        verbose_name_plural = "Kingdom Business IGAs"

    def __str__(self):
        return self.title


class DigitalMinistrySummary(SingletonModel):
    heading = models.CharField(max_length=150, blank=True, default="Digital Ministry")
    body = models.TextField(blank=True)
    cta_text = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Digital Ministry (singleton)"

    def __str__(self):
        return self.heading


# ---------------------------------------------------------------------------
# Where We Work — regions & hubs with UPG data and map pins
# ---------------------------------------------------------------------------

class RegionHub(models.Model):
    STATUS_CHOICES = (
        ("engaged", "Engaged"),
        ("emerging", "Emerging"),
        ("pioneering", "Pioneering"),
        ("vision", "Vision stage"),
    )

    name = models.CharField(max_length=120)                # Tigray, Gondar, Arsi, Somali…
    region_type = models.CharField(max_length=20, choices=(("region", "Region"), ("hub", "Hub")), default="region")
    upg_count = models.PositiveSmallIntegerField(default=0, help_text="Unreached People Groups engaged here.")
    total_churches = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="engaged")
    summary = models.TextField(blank=True)
    # Map pin data
    latitude = models.FloatField(default=9.145)   # Ethiopia default
    longitude = models.FloatField(default=40.489)
    pin_label = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return f"{self.name} ({self.get_region_type_display()})"


# ---------------------------------------------------------------------------
# Vision 100DM35 — MEL indicator tracker (editable by MEL admins)
# ---------------------------------------------------------------------------

class MelIndicator(models.Model):
    code = models.CharField(max_length=30, unique=True, help_text="e.g. V1.1")
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=40, blank=True, default="count")
    direction = models.CharField(
        max_length=10, choices=(("increase", "Increase"), ("decrease", "Decrease")), default="increase",
        help_text="Good direction of travel — affects % toward target.",
    )
    baseline_2025 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_2030 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pillar = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("code",)
        verbose_name = "MEL Indicator"
        verbose_name_plural = "MEL Indicators (Vision 100DM35)"

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def progress_pct(self) -> int:
        """Percentage of the way from baseline to the 2030 target (0–100+)."""
        base = float(self.baseline_2025)
        cur = float(self.current_value)
        tgt = float(self.target_2030)
        delta = tgt - base
        if delta == 0:
            return 100 if cur >= tgt else 0
        pct = (cur - base) / delta * 100
        if self.direction == "decrease":
            pct = (base - cur) / (base - tgt) * 100 if base != tgt else 0
        return max(0, min(999, round(pct)))


# ---------------------------------------------------------------------------
# Impact & Stories — news, stories and testimonies with safety review flag
# ---------------------------------------------------------------------------

class Story(models.Model):
    kind = models.CharField(max_length=20, choices=(("news", "News"), ("story", "Story"), ("testimony", "Testimony")), default="story")
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField(blank=True, help_text="Rich text (HTML).")
    cover_image = models.ImageField(upload_to="stories/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    region = models.ForeignKey(RegionHub, on_delete=models.SET_NULL, null=True, blank=True, related_name="stories")
    region_tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated free tags.")
    published_at = models.DateField(null=True, blank=True)
    safety_review_status = models.CharField(
        max_length=20,
        choices=(("pending", "Safety review pending"), ("approved", "Safety reviewed & approved"), ("blocked", "Blocked (do not publish)")),
        default="pending",
        help_text="Only 'approved' items are shown publicly.",
    )
    is_featured = models.BooleanField(default=False)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags, e.g. 'DMM, Tigray'.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)[:200]
        slug = base_slug
        i = 2
        qs = Story.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"
            i += 1
        self.slug = slug
        super().save(*args, **kwargs)

    def clean(self):
        # Safety review gate — pending/blocked items must never be publicly visible by accident.
        if self.safety_review_status != "approved" and self.is_featured:
            raise ValidationError({"is_featured": "Only safety-approved items can be featured."})

    class Meta:
        ordering = ("-published_at", "-created_at")

    def __str__(self):
        return self.title
