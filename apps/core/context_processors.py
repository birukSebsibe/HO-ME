from apps.core.models import SiteSetting


def site_settings(request):
    return {"site": SiteSetting.load()}
