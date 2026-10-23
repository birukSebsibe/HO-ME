"""
Request middleware for the audit trail.

Makes the current request visible to audit signal receivers, so model saves
anywhere in a request can be attributed to the acting staff member and IP.

It also records brute-force lockouts: when django-axes blocks a login attempt,
the lockout response is returned before the login view runs, so this is the
only place the event can be captured.
"""

from django.urls import reverse

from .audit import record, set_current_request


class AuditRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        try:
            response = self.get_response(request)
            self._audit_lockout(request, response)
            return response
        finally:
            set_current_request(None)

    @staticmethod
    def _audit_lockout(request, response):
        """Record axes brute-force lockouts (403/429 on the login route)."""
        from .models import AuditLog

        if response.status_code not in (403, 429) or response.streaming:
            return
        # The login view already recorded this attempt as a lockout.
        if getattr(request, "_audit_lockout_recorded", False):
            return
        try:
            login_path = reverse("admin_portal:login")
        except Exception:
            return
        if request.path != login_path:
            return
        record(
            AuditLog.LOCKOUT,
            username=(request.POST.get("username", "")[:150] if request.method == "POST" else ""),
            request=request,
            note="Blocked by brute-force protection (django-axes)",
        )
