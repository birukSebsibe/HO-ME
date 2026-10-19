from django.urls import path

from . import views

app_name = "security"

urlpatterns = [
    path("login/", views.HOMESecurityLoginView.as_view(), name="login"),
    path("logout/", views.totp_logout, name="logout"),
    path("password-reset/", views.HOMESecurityPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.HOMESecurityPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", views.HOMESecurityPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", views.HOMESecurityPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
