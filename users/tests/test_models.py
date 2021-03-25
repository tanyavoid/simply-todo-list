from django.test import TestCase
from django.contrib.auth import get_user_model

from users.models import UserSettings

UserModel = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='test', email='test@example.com', password='Rf27knzpWD'
        )

    def test_user_settings_created(self):
        self.assertTrue(hasattr(self.user, 'settings'))

    def test_settings_values_access(self):
        settings = self.user.settings
        self.assertTrue(hasattr(settings, 'language'))
        self.assertTrue(hasattr(settings, 'theme'))
        self.assertTrue(settings.theme == self.user.get_settings_value('theme'))


class UserSettingsModelTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='test', email='test@example.com', password='Rf27knzpWD'
        )

    def test_user_default_language(self):
        default = UserSettings._meta.get_field('language').get_default()
        self.assertTrue(self.user.settings.language == default)

    def test_user_default_theme(self):
        default = UserSettings._meta.get_field('theme').get_default()
        self.assertTrue(self.user.settings.theme == default)

    def test_user_theme_change(self):
        default = UserSettings._meta.get_field('theme').get_default()
        self.user.settings.theme = 1
        self.assertFalse(self.user.settings.theme == default)

    def test_user_clanguage_change(self):
        user_language = self.user.settings.language
        language_to_set = 'ru' if user_language == 'en' else 'en'
        self.assertFalse(user_language == language_to_set)
        self.user.settings.language = language_to_set
        self.assertTrue(self.user.settings.language == language_to_set)
