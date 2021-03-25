from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from todo.models import Todo

UserModel = get_user_model()


class TodoModelTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username='test', email='test@example.com', password='Rf27knzpWD'
        )
        self.obj = Todo.objects.create(text='Do this', owner=self.user)
        self.obj_done = Todo.objects.create(
            text='Do that',
            owner=self.user,
            is_done=True,
            date_done=(timezone.now() + timezone.timedelta(days=1)),
        )

    def test_obj_slug_created_and_unique(self):
        self.assertTrue(self.obj.slug)
        self.assertEqual(len(self.obj.slug), 5)
        self.assertTrue(self.obj_done.slug)
        self.assertEqual(len(self.obj_done.slug), 5)
        self.assertTrue(self.obj.slug != self.obj_done.slug)

    def test_todo_queryset(self):
        self.assertEqual(Todo.objects.count(), 2)
        Todo.objects.create(text='Do that', owner=self.user)
        self.assertEqual(Todo.objects.count(), 3)

        qs = Todo.objects.filter(slug=self.obj.slug)
        self.assertEqual(qs.count(), 1)

    def test_obj_is_done_value(self):
        self.assertFalse(self.obj.is_done)
        self.obj.is_done = True
        self.assertTrue(self.obj.is_done)

    def test_obj_dates(self):
        self.assertTrue(self.obj.date_added)
        self.assertFalse(self.obj.date_done)

        self.assertTrue(self.obj_done.date_added)
        self.assertTrue(self.obj_done.date_added < self.obj_done.date_done)
