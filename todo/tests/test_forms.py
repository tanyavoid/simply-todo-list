from django.test import TestCase
from django.contrib.auth import get_user_model

from todo.models import Todo
from todo.forms import TodoForm

UserModel = get_user_model()


class TodoFormTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='test',
            email='testuser@example.com',
            password='Rf27knzpWD',
        )

    def test_form_is_valid(self):
        obj = Todo.objects.create(text='Do this', owner=self.user)
        data = {'text': obj.text}
        form = TodoForm(data=data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('text'), obj.text)
        self.assertNotEqual(form.cleaned_data.get('text'), 'Sleep')

    def test_form_without_text_is_not_valid(self):
        form = TodoForm(data={})

        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
        self.assertEqual(len(form.errors), 1)

    def test_form_label(self):
        form = TodoForm()
        self.assertTrue(form.fields['text'].label == '')
