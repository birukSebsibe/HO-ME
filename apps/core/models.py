from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class SingletonModel(models.Model):
    """A model of which only one row may exist."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding and self.__class__.objects.exclude(pk=self.pk).exists():
            raise ValidationError(f"Only one {self.__class__.__name__} instance is allowed.")
        if not self.__class__.objects.exists() or self.pk == self.__class__.objects.get().pk:
            super().save(*args, **kwargs)
        else:
            # Keep only the first row.
            self.pk = self.__class__.objects.first().pk
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSetting(SingletonModel):
    """Global, fully editable site configuration (hero, counters, contact, footer…)."""

    # --- Identity
    site_name = models.CharField(max_length=120, default="Horn of Africa Missions Engagers (HO-ME)")
    site_tagline = models.CharField(max_length=200, blank=True, default="Mobilizing. Catalyzing. Multiplying. Sustaining.")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    favicon = models.ImageField(upload_to="branding/", blank=True, null=True)

    # --- Hero: option A / B toggle
    hero_variant = models.CharField(
        max_length=1,
        choices=(("A", "Option A (split panel)"), ("B", "Option B (full-bleed photo)")),
        default="A",
        help_text="Which hero layout the homepage should render.",
    )
    headline_a = models.CharField(
        max_length=250,
        blank=True,
        default="Reaching the Unreached of the Horn of Africa",
    )
    headline_b = models.CharField(
        max_length=250,
        blank=True,
        default="Every Unreached People Group. Every Generation. Every Nation.",
    )
    subheadline = models.TextField(
        blank=True,
        default=(
            "HO-ME mobilizes, catalyzes, multiplies and sustains gospel movements among the "
            "unreached peoples of the Horn of Africa."
        ),
    )
    hero_cta_text_1 = models.CharField(max_length=80, blank=True, default="Partner With Us")
    hero_cta_url_1 = models.CharField(max_length=200, blank=True, default="/get-involved/")
    hero_cta_text_2 = models.CharField(max_length=80, blank=True, default="Explore Our Work")
    hero_cta_url_2 = models.CharField(max_length=200, blank=True, default="/what-we-do/")

    # --- Impact counter strip (all live-editable)
    counter_churches = models.PositiveIntegerField(default=23000, help_text="e.g. 23,000+ churches planted")
    counter_years = models.PositiveIntegerField(default=20, help_text="Years of ministry")
    counter_upgs = models.PositiveIntegerField(default=8, help_text="Unreached People Groups engaged")
    counter_hubs = models.PositiveIntegerField(default=10, help_text="Training hubs (8–12)")
    counter_network = models.PositiveIntegerField(default=4000, help_text="Networked churches")

    # --- Contact
    contact_email = models.EmailField(blank=True, default="info@ho-me.org")
    contact_phone = models.CharField(max_length=40, blank=True, default="+251 911 000 000")
    contact_address = models.TextField(blank=True, default="Addis Ababa, Ethiopia")
    contact_map_embed_url = models.URLField(blank=True, help_text="Optional Google Maps embed URL.")

    # --- Social
    social_facebook = models.URLField(blank=True)
    social_x = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_youtube = models.URLField(blank=True)
    social_linkedin = models.URLField(blank=True)

    # --- Footer
    privacy_policy_url = models.CharField(max_length=200, blank=True, default="/privacy/")
    transparency_url = models.CharField(max_length=200, blank=True, default="/transparency/")
    footer_note = models.TextField(blank=True, default="HO-ME is a faith-based missions movement serving the peoples of the Horn of Africa.")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings (singleton)"

    def __str__(self):
        return "Global site settings"

    @property
    def active_headline(self):
        return self.headline_b if self.hero_variant == "B" else self.headline_a


class PartnerLogo(models.Model):
    site = models.ForeignKey(SiteSetting, on_delete=models.CASCADE, related_name="partner_logos")
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to="partners/")
    url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return self.name


class LeadershipProfile(models.Model):
    site = models.ForeignKey(SiteSetting, on_delete=models.CASCADE, related_name="leaders")
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return f"{self.name} — {self.role}"


class TimelineMilestone(models.Model):
    site = models.ForeignKey(SiteSetting, on_delete=models.CASCADE, related_name="milestones")
    year = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text="Lucide icon name, e.g. 'sprout', 'map-pin'.")
    order = models.PositiveSmallIntegerField(default=0)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ("year", "order")
        verbose_name_plural = "Timeline milestones"

    def __str__(self):
        return f"{self.year} — {self.title}"


class CoreValue(models.Model):
    site = models.ForeignKey(SiteSetting, on_delete=models.CASCADE, related_name="core_values")
    number = models.PositiveSmallIntegerField(default=1, help_text="Card number 1-4 shown on the About page.")
    title = models.CharField(max_length=120)
    body = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text="Lucide icon name.")

    class Meta:
        ordering = ("number",)

    def __str__(self):
        return self.title
