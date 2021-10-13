from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from todo.views import (
    home,
    edit,
    delete,
    change_language,
    sort,
    try_view,
    serialized_items_view,
)

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
    path('try/', try_view, name='try'),
    path('serialized/', serialized_items_view, name='serialized'),
    prefix_default_language=False,
)
