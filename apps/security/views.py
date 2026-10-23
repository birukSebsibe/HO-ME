"""
Admin portal login/logout for HO-ME.

Simple username + password sign-in (django-axes protected against brute force).
"""

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from apps.core.models import SiteSetting


class HOMESecurityBrandingMixin:
    """
    Django's auth views (LoginView etc.) put *their* `site` (a RequestSite)
    into the template context, shadowing our SiteSetting. Re-impose our brand
    so templates get site.logo / site.site_name from the CMS settings.
    """

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["site"] = SiteSetting.load()
        return ctx

class HOMESecurityLoginForm(AuthenticationForm):
    """Plain username + password form (axes protected via AUTHENTICATION_BACKENDS)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"autofocus": True, "autocomplete": "username"})
        self.fields["password"].widget.attrs.update({"autocomplete": "current-password"})


class HOMESecurityLoginView(HOMESecurityBrandingMixin, DjangoLoginView):
    """Login view for the admin portal (csrf + axes protected)."""

    template_name = "security/login.html"
    redirect_authenticated_user = True
    form_class = HOMESecurityLoginForm
    extra_context = {"site_header": settings.ADMIN_SITE_HEADER}

    def form_invalid(self, form):
        # Audit: failed sign-in. When axes has locked the attempt out it also
        # raises inside the view, so record that as a LOCKOUT event (the
        # middleware skips its own lockout entry in that case).
        from .audit import record
        from .models import AuditLog
        if getattr(self.request, "axes_locked_out", False):
            record(
                AuditLog.LOCKOUT,
                username=self.request.POST.get("username", "")[:150],
                request=self.request,
                note="Blocked by brute-force protection (django-axes)",
            )
            self.request._audit_lockout_recorded = True
        else:
            record(
                AuditLog.LOGIN_FAILED,
                username=self.request.POST.get("username", "")[:150],
                request=self.request,
                note="Invalid credentials",
            )
        return super().form_invalid(form)

    def get_success_url(self):
        # Land on the admin dashboard after sign-in
        try:
            return reverse("admin_portal:index")
        except Exception:
            return "/"


def totp_logout(request):
    """Log out and return to the login page (kept name for url compat)."""
    logout(request)
    return redirect(reverse("admin_portal:login"))


# ---------------------------------------------------------------------------
# Forgot-password (email reset) flow — reuses Django's secure token system
# ---------------------------------------------------------------------------

class HOMESecurityPasswordResetView(HOMESecurityBrandingMixin, PasswordResetView):
    template_name = "security/password_reset_form.html"
    email_template_name = "security/password_reset_email.html"
    subject_template_name = "security/password_reset_subject.txt"
    success_url = reverse_lazy("security:password_reset_done")
    extra_context = {"site_header": settings.ADMIN_SITE_HEADER}

    def form_valid(self, form):
        # Audit: someone requested a password reset for this account.
        from .audit import record
        from .models import AuditLog
        record(
            AuditLog.PASSWORD_RESET_REQUESTED,
            username=form.cleaned_data.get("username", "")[:150],
            request=self.request,
        )
        return super().form_valid(form)


class HOMESecurityPasswordResetDoneView(HOMESecurityBrandingMixin, PasswordResetDoneView):
    template_name = "security/password_reset_done.html"
    extra_context = {"site_header": settings.ADMIN_SITE_HEADER}


class HOMESecurityPasswordResetConfirmView(HOMESecurityBrandingMixin, PasswordResetConfirmView):
    template_name = "security/password_reset_confirm.html"
    success_url = reverse_lazy("security:password_reset_complete")
    extra_context = {"site_header": settings.ADMIN_SITE_HEADER}

    def form_valid(self, form):
        # Audit: the password was actually changed via a reset link.
        from .audit import record
        from .models import AuditLog
        record(AuditLog.PASSWORD_RESET, user=form.user, request=self.request)
        return super().form_valid(form)


class HOMESecurityPasswordResetCompleteView(HOMESecurityBrandingMixin, PasswordResetCompleteView):
    template_name = "security/password_reset_complete.html"
    extra_context = {"site_header": settings.ADMIN_SITE_HEADER}
