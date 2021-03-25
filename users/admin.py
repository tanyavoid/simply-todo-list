from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserSettings

admin.site.register(User, UserAdmin)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'get_username', 'language', 'theme']

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'
