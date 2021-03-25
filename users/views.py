import io

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, translate_url
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import activate, LANGUAGE_SESSION_KEY, gettext as _

from .models import User
from .forms import RegistrationForm, EmailForm, LoginForm
from .utils import write_txt, write_csv, write_md, write_json


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.is_active}'


token_generator = TokenGenerator()


def send_activation_link(request, user, first=True):
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    mail_subject = _('Activate your account')
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    html_message = render_to_string(
        'auth/registration_activation_email.html',
        {
            'user': user,
            'domain': current_site,
            'uidb64': uid,
            'token': token,
            'protocol': protocol,
            'first': first,
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        mail_subject,
        plain_message,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
        html_message=html_message,
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            send_activation_link(request, user)
            msg = _('Welcome! Please check your email to complete registration.')
            messages.info(request, _(msg))
            return redirect('login')

        elif User.objects.filter(email__iexact=email, is_active=False).exists():
            return render(request, 'auth/registration_activation_error.html')

        return redirect(request.path_info)

    return render(request, 'auth/auth.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        msg = _('Great! Now you can login and create your todos.')
        messages.info(request, msg)
        return redirect('login')
    else:
        return render(request, 'auth/registration_activation_error.html')


def resend_activation(request):
    if request.user.is_authenticated:
        messages.info(request, _('Your account is already activated.'))
        return redirect('home')

    form = EmailForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email', None)
        try:
            user = User.objects.get(email__iexact=email)
            if user.is_active:
                messages.info(request, _('Your account is already activated.'))
                return redirect('login')
            send_activation_link(request, user, first=False)
            messages.info(
                request, _('Please check your email for the activation link.')
            )
            return redirect('login')
        except User.DoesNotExist:
            msg = _('Please entered the address you registered with.')
            messages.error(request, msg)
            return redirect(request.path_info)
    context = {'form': form}
    return render(request, 'auth/registration_activation_resend.html', context)


class LoginUserView(LoginView):
    template_name = 'auth/auth.html'
    redirect_authenticated_user = True
    form_class = LoginForm

    def get_success_url(self):
        url = super().get_success_url()
        user = self.request.user
        if user.is_authenticated:
            user_language = user.settings.language
            url = translate_url(url, user_language)
            activate(user_language)
            if hasattr(self.request, 'session'):
                self.request.session[LANGUAGE_SESSION_KEY] = user_language
        return url


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    old = request.POST.get('old_password')
    new = request.POST.get('new_password1')

    if form.is_valid():
        old = request.POST.get('old_password')
        new = request.POST.get('new_password1')
        if old == new:
            messages.info(request, _('You haven’t changed your password.'))
        else:
            user = form.save()
            update_session_auth_hash(request, user)
            messages.info(request, _('Your password was successfully updated!'))
        return redirect('home')

    return render(request, 'auth/password_change.html', {'form': form})


@login_required
def user_settings(request):
    settings = request.user.settings
    context = {
        'theme': settings.theme,
        'language': settings.language,
    }
    return render(request, 'user_settings.html', context)


@login_required
def change_theme(request):
    if 'theme' in request.POST:
        request.user.settings.theme = int(request.POST.get('theme'))
        request.user.settings.save()
    return redirect('user-settings')


@login_required
def change_user_language(request):
    if 'language' in request.POST:
        language = request.POST.get('language')
        request.user.settings.language = language
        request.user.settings.save()
        activate(language)
        settings_page = reverse('user-settings')
        response = HttpResponseRedirect(settings_page)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
    return redirect('user-settings')


@login_required
def export(request):
    if request.method == 'POST':
        user = request.user
        not_done = user.todo_set.filter(is_done=False).order_by('order', '-date_added')
        done = user.todo_set.filter(is_done=True).order_by('date_done')
        todo_list = list(not_done) + list(done)
        fmt = request.POST.get('format')
        stream = io.StringIO()

        if fmt == 'txt':
            content_type = 'text/plain'
            write_txt(todo_list, stream)
        elif fmt == 'md':
            content_type = 'text/markdown'
            write_md(todo_list, stream)
        elif fmt == 'csv':
            content_type = 'text/csv'
            write_csv(todo_list, stream)
        elif fmt == 'json':
            content_type = 'application/json'
            write_json(todo_list, stream)

        stream.seek(0)
        response = HttpResponse(stream, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename=todos.{fmt}'
        stream.close()
        return response

    return redirect('user-settings')
