from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Username or email'),
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    _(
                        'Please enter a correct username/email and password. Note that both fields are case-sensitive.'
                    ),
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            link_text = _('request a new one')
            link = f'<a href="/resend-activation/">{link_text}</a>'
            msg = _(
                'Your account is not activated.\nPlease check your email for the activation link or {}.'
            )
            raise ValidationError(msg.format(link))


class RegistrationForm(UserCreationForm):
    username = forms.RegexField(
        label=_('Username'),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_('30 chars or fewer. Letters, digits and ' '@/./+/-/_'),
        error_messages={
            'invalid': _(
                'This value may contain only letters, numbers and '
                '@/./+/-/_ characters'
            )
        },
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'true',
                'autofocus': 'autofocus',
                'placeholder': '',
            }
        ),
    )

    email = forms.EmailField(label=_('Email'))

    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': 'true',
                'placeholder': '',
            }
        ),
        help_text=_('Make a good one'),
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'type': 'password',
                'required': True,
                'placeholder': '',
            }
        ),
        help_text=_('Repeat a good one'),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EmailForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'autofocus': 'autofocus',
            }
        ),
    )
