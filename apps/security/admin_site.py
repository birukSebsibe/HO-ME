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

    def has_permission(self, request):
        """Staff + active only."""
        return request.user.is_active and request.user.is_staff

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
        return ctx


admin_site = HOMESecurityAdminSite(name="admin_portal")
