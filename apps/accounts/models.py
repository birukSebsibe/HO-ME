import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class ComplexityValidator:
    """Password must contain upper, lower, digit and (at least 10 chars total)."""

    def validate(self, password, user=None):
        if not (
            re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"\d", password)
        ):
            raise ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, and one digit.",
                code="password_no_complexity",
            )

    def get_help_text(self):
        return "Your password must contain upper- and lowercase letters and at least one digit."


class User(AbstractUser):
    """Custom user: adds a MEL-admin flag used to gate the Vision 100DM35 editor."""

    is_mfa_verified = models.BooleanField(default=False, help_text="Set automatically once a TOTP device is confirmed.")
    is_mel_admin = models.BooleanField(
        default=False,
        help_text="Designated MEL staff allowed to edit Vision 100DM35 indicator data.",
    )
    job_title = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def has_mfa(self):
        return self.is_mfa_verified

    def get_full_display_name(self):
        return self.get_full_name() or self.username


class SubmissionBase(models.Model):
    """Common fields for every interactive public form on the site."""

    STATUS = (("new", "New"), ("in_review", "In review"), ("closed", "Closed"))
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    region_hub = models.CharField(max_length=120, blank=True, help_text="Region or hub of interest.")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.get_kind_display()} — {self.full_name} ({self.created_at:%Y-%m-%d})"

    def get_kind_display(self):
        return self._meta.verbose_name


class PrayerSignup(SubmissionBase):
    frequency = models.CharField(max_length=20, choices=(("weekly", "Weekly"), ("monthly", "Monthly"), ("one_off", "One-off")), default="weekly")
    topics_of_interest = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = "Prayer signup"
        verbose_name_plural = "Prayer signups"


class ChurchPartnershipApplication(SubmissionBase):
    church_name = models.CharField(max_length=200)
    denomination = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)
    partnership_interest = models.CharField(
        max_length=30,
        choices=(
            ("prayer", "Prayer partner"),
            ("giving", "Giving partner"),
            ("sending", "Sending / mobilizing partner"),
            ("hosting", "HOST school host"),
            ("other", "Other"),
        ),
        default="prayer",
    )

    class Meta:
        verbose_name = "Church partnership application"


class VolunteerStaffApplication(SubmissionBase):
    APPLICATION_KIND = (("volunteer", "Volunteer"), ("staff", "Staff"))
    kind = models.CharField(max_length=10, choices=APPLICATION_KIND, default="volunteer")
    skills = models.CharField(max_length=250, blank=True)
    availability = models.CharField(max_length=120, blank=True)
    references = models.TextField(blank=True, help_text="Names & contacts of referees.")
    cv_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Volunteer / staff application"


class GivingOption(models.Model):
    """Editable giving options: bank accounts, mobile money, in-kind, etc."""

    KIND = (("bank", "Bank transfer"), ("mobile", "Mobile money"), ("inkind", "In-kind"), ("online", "Online"))
    kind = models.CharField(max_length=10, choices=KIND, default="bank")
    title = models.CharField(max_length=150)
    details = models.TextField(blank=True, help_text="e.g. Account name, number, SWIFT, branches.")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.title
