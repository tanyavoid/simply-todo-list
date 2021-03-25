from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import get_language

UserModel = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='test',
            email='testuser@example.com',
        )
        self.raw_password = 'Rf27knzpWD'
        self.user.set_password(self.raw_password)
        self.user.save()
        self.credentials = {'password': self.raw_password}

    def test_login_email(self):
        self.credentials['username'] = self.user.email
        logged_in = self.client.login(**self.credentials)
        self.assertTrue(logged_in)

    def test_login_username(self):
        self.credentials['username'] = self.user.username
        logged_in = self.client.login(**self.credentials)
        self.assertTrue(logged_in)

    def test_user_settings_page(self):
        self.client.force_login(self.user)
        url = reverse('user-settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('user_settings.html')

    def test_user_changes_language(self):
        self.client.force_login(self.user)
        url = reverse('change-user-language')
        user_language = self.user.settings.language
        language_to_set = 'ru' if user_language == 'en' else 'en'
        self.assertFalse(user_language == language_to_set)
        response = self.client.post(url, {'language': language_to_set})
        self.user.settings.refresh_from_db()
        self.assertTrue(self.user.settings.language == language_to_set)
        self.assertEqual(response.status_code, 302)

    def test_user_changes_theme(self):
        self.client.force_login(self.user)
        user_theme = self.user.settings.theme
        theme_to_set = 1 if user_theme == 0 else 0
        self.assertFalse(user_theme == theme_to_set)
        url = reverse('change-theme')
        response = self.client.post(url, {'theme': theme_to_set})
        self.user.settings.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.settings.theme == theme_to_set)

    def test_file_export(self):
        self.client.force_login(self.user)
        url = reverse('export')
        formats = ['txt', 'md', 'csv', 'json']
        for fmt in formats:
            response = self.client.post(url, {'format': fmt})
            content = f'attachment; filename=todos.{fmt}'
            self.assertEquals(response.get('Content-Disposition'), content)

    def test_change_password(self):
        self.client.force_login(self.user)
        url = reverse('change-password')
        old_hash = self.user.password
        new = 'ThQjLcrN'
        data = {
            'old_password': self.raw_password,
            'new_password1': new,
            'new_password2': new,
        }
        response = self.client.post(url, data)
        self.user.refresh_from_db()
        self.assertFalse(self.user.password == old_hash)


class UserViewsAnonymousUserTests(TestCase):
    def test_user_settings_redirect(self):
        url = reverse('user-settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_change_password_redirect(self):
        url = reverse('change-password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
