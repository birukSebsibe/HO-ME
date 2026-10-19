from django.apps import AppConfig

class SecurityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
    verbose_name = "HO-ME Admin Security"

    def ready(self):
        pass
