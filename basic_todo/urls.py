from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from todo.views import home, edit, delete, change_language, sort, trial

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('', home, name='home'),
    path('', include('users.urls')),
    path('edit/<slug:slug>/', edit, name='edit'),
    path('delete/<slug:slug>/', delete, name='delete'),
    path('change-language/', change_language, name='change-language'),
    path('sort/', sort, name='sort'),
    path('try/', trial, name='try'),

    prefix_default_language=False
)
