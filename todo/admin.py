from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['text', 'owner', 'is_done', 'slug', 'date_added']

    class Meta:
        model = Todo

