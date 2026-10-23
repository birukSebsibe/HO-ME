"""
Audit trail models for the HO-ME admin portal.

AuditLog is the single, append-only record of everything worth reviewing when
something goes wrong: who signed in (and from where), who changed what content,
who approved/blocked stories, failed sign-in attempts, password resets, etc.
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class AuditLog(models.Model):
    """One recorded administrative/security event."""

    # ---- event kinds (kept coarse so filters stay useful) ----
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    LOCKOUT = "lockout"
    LOGOUT = "logout"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET = "password_reset"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYSTEM = "system"

    ACTIONS = (
        (LOGIN, "Signed in"),
        (LOGIN_FAILED, "Failed sign-in"),
        (LOCKOUT, "Locked out (brute-force protection)"),
        (LOGOUT, "Signed out"),
        (PASSWORD_RESET_REQUESTED, "Password reset requested"),
        (PASSWORD_RESET, "Password reset completed"),
        (CREATE, "Created"),
        (UPDATE, "Updated"),
        (DELETE, "Deleted"),
        (SYSTEM, "System event"),
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
        help_text="Staff account that performed the action (blank for public/anonymous events).",
    )
    username = models.CharField(max_length=150, blank=True, db_index=True)
    action = models.CharField(max_length=32, choices=ACTIONS, db_index=True)

    # Optional link to the object the action was performed on
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.CharField(max_length=64, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField(max_length=255, blank=True)

    # Request metadata (best effort — review aids)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = "Audit log entry"
        verbose_name_plural = "Audit log"

    def __str__(self):
        who = self.username or "—"
        return f"{self.timestamp:%Y-%m-%d %H:%M} · {who} · {self.get_action_display()} · {self.object_repr[:80]}"
