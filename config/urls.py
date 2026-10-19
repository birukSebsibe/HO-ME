from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import include, path
from django.views.i18n import set_language
from django.views.static import serve as django_serve

from apps.core import views as core_views
from apps.security import views as security_views
from apps.security.admin_site import admin_site

ADMIN_URL = settings.ADMIN_URL  # e.g. "admin-portal/"

urlpatterns = [
    # Public website
    path("", core_views.home, name="home"),
    path("about/", core_views.about, name="about"),
    path("what-we-do/", core_views.what_we_do, name="what-we-do"),
    path("where-we-work/", core_views.where_we_work, name="where-we-work"),
    path("vision-100dm35/", core_views.vision, name="vision"),
    path("impact/", core_views.impact, name="impact"),
    path("impact/story/<slug:slug>/", core_views.story_detail, name="story-detail"),
    path("library/", core_views.library, name="library"),
    path("get-involved/", core_views.get_involved, name="get-involved"),
    path("privacy/", core_views.privacy, name="privacy"),
    path("transparency/", core_views.transparency, name="transparency"),

    # Interactive public forms
    path("submit/prayer/", core_views.prayer_signup, name="prayer-signup"),
    path("submit/partnership/", core_views.partnership, name="partnership"),
    path("submit/volunteer/", core_views.volunteer, name="volunteer"),
    path("library/<slug:slug>/request-access/", core_views.request_access, name="request-access"),
    path("library/<slug:slug>/download/", core_views.resource_download, name="resource-download"),

    # Admin portal (custom URL)    path(ADMIN_URL + "", include("apps.security.urls")),
    path(ADMIN_URL, admin_site.urls),

    # Language switching (English / Amharic / Oromifa)
    path("setlang/", set_language, name="set_language"),

    # Robots / health
    path("robots.txt", core_views.robots, name="robots"),
    path("health/", core_views.health, name="health"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("static/<path:path>", django_serve, {"document_root": settings.STATIC_ROOT}),
]
