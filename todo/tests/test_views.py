from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import get_language

from todo.models import Todo

UserModel = get_user_model()


class BasicHomePageTests(SimpleTestCase):
    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_home_page_contains_correct_content(self):
        response = self.client.get('/')
        self.assertContains(response, 'You need an account')


class TodoViewsLoggedInUserTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='test',
            email='testuser@example.com',
            password='Rf27knzpWD',
        )
        self.client.force_login(self.user)
        self.obj = Todo.objects.create(text='Do this', owner=self.user)

    def test_home_view_GET(self):
        response = self.client.get('/')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New to-do item')

    def test_adding_todo(self):
        text = 'Do something else'
        response = self.client.post('/', {'text': text})
        self.assertTrue(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 2)
        self.assertTrue(Todo.objects.filter(text=text).exists())

    def test_adding_todo_no_data(self):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(Todo.objects.count(), 1)

    def test_edit_view(self):
        url = reverse('edit', kwargs={'slug': self.obj.slug})
        text = 'Do that'
        self.assertFalse(self.obj.text == text)
        response = self.client.post(url, {'text': text})
        self.obj.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.obj.text == text)

    def test_delete_view(self):
        url = reverse('delete', kwargs={'slug': self.obj.slug})
        response = self.client.get(url)
        self.assertEqual(Todo.objects.count(), 0)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(slug=self.obj.slug).exists())

    def test_detele_404(self):
        slug = 'abc123'
        url = reverse('delete', kwargs={'slug': slug})
        response = self.client.get(url)
        self.assertEqual(Todo.objects.filter(slug=slug).count(), 0)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Todo.objects.count(), 1)


class TodoViewsAnonymousUserTests(TestCase):
    def test_user_sees_homepage(self):
        response = self.client.get('/')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'need an account')

    def test_language_change(self):
        url = reverse('change-language')
        current_language = get_language()
        language_to_set = 'ru' if current_language == 'en' else 'en'
        response = self.client.post(url, {'language': language_to_set})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_language(), language_to_set)

    def test_edit_view_redirect(self):
        url = reverse('edit', kwargs={'slug': 'abc123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_delete_view_redirect(self):
        url = reverse('delete', kwargs={'slug': 'abc123'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
