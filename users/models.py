from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import get_language, gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'({self.username}, {self.email})'

    def get_settings_value(self, key):
        return vars(self.settings).get(key)


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    language = models.CharField(
        max_length=2,
        choices=[('en', _('English')), ('ru', _('Russian'))],
        default=get_language,
    )
    theme = models.IntegerField(choices=[(0, _('Dark')), (1, _('Light'))], default=0)

    def __str__(self):
        return f'{self.user.email} (account settings)'

    class Meta:
        verbose_name = 'User settings'
        verbose_name_plural = verbose_name


@receiver(post_save, sender=User)
def create_or_update_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)
    instance.settings.save()
