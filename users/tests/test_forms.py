from django.test import SimpleTestCase

from users.forms import LoginForm, RegistrationForm, EmailForm


class UserFormsTests(SimpleTestCase):
    def test_login_form_label(self):
        form = LoginForm()
        self.assertTrue(form.fields['username'].label == 'Username or email')

    def test_registration_form_help_text(self):
        form = RegistrationForm()
        help_text_uname = '30 chars or fewer. Letters, digits and @/./+/-/_'
        help_text_pw1 = 'Make a good one'
        self.assertTrue(form.fields['username'].help_text == help_text_uname)
        self.assertTrue(form.fields['password1'].help_text == help_text_pw1)

    def test_email_form_is_valid(self):
        form = EmailForm(data={'email': 'user@example.com'})
        self.assertTrue(form.is_valid())

    def test_email_form_is_invalid(self):
        form = EmailForm(data={'email': 'abc123'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
