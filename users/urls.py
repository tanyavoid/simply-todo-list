from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from .views import (
    register,
    activate_account,
    resend_activation,
    user_settings,
    change_password,
    change_theme,
    change_user_language,
    export,
    LoginUserView,
)
from .forms import LoginForm

urlpatterns = [
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate-account'),
    path('resend-activation/', resend_activation, name='resend-activation'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('settings/', user_settings, name='user-settings'),
    path('change-password/', change_password, name='change-password'),
    path('change-theme/', change_theme, name='change-theme'),
    path('change-user-language/', change_user_language, name='change-user-language'),
    path('export/', export, name='export'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path(
        "reset-password/",
        PasswordResetView.as_view(
            template_name="auth/password_reset.html",
            html_email_template_name="auth/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "reset-password/done/",
        PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset-password-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
