from django.db import models
from django.utils import timezone
from django.conf import settings

from .utils import get_random_string


class Todo(models.Model):
    text = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    slug = models.SlugField(unique=True, null=False)
    date_added = models.DateTimeField(default=timezone.now)
    date_done = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"Todo('{self.text}')"

    def save(self, *args, **kwargs):
        if not self.slug:
            while True:
                slug = get_random_string(5)
                if not Todo.objects.filter(slug=slug).exists():
                    break
            self.slug = slug
        super().save(*args, **kwargs)
