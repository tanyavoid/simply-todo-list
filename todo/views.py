import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Todo
from .forms import TodoForm, TodoTryForm
from .serializers import TodoSerializer


def home(request):
    '''Add item + list view for authenticated users; hello page for others.'''
    user = request.user

    if user.is_authenticated:
        form = TodoForm(request.POST or None)

        if form.is_valid():
            todo = form.save(commit=False)
            todo.owner = user
            todo.save()
            return redirect('home')

        if request.method == 'POST' and 'is_done' in request.POST:
            is_done_value = request.POST.get('is_done')
            if 'unchecked' in is_done_value:
                slug = is_done_value.split('-')[0]
                todo = Todo.objects.get(slug=slug)
                todo.is_done = False
                todo.date_done = None
                todo.date_added = timezone.now()
                todo.order = 0
            else:
                todo = Todo.objects.get(slug=is_done_value)
                todo.is_done = True
                todo.date_done = timezone.now()
            todo.save()
            return redirect('home')

        user_todos = Todo.objects.filter(owner=user)
        not_done = user_todos.filter(is_done=False).order_by(
            'order', '-date_added'
        )
        done = user_todos.filter(is_done=True).order_by('-date_done')
        todo_list = list(not_done) + list(done)
        context = {'form': form, 'todo_list': todo_list}
    else:
        context = {}

    return render(request, 'index.html', context)


@login_required
def edit(request, slug):
    todo = get_object_or_404(Todo, slug=slug)
    form = TodoForm(request.POST or None, instance=todo)

    if form.is_valid():
        form.save()
        return redirect('home')

    return render(request, 'index.html', {'form': form})


@login_required
def delete(request, slug):
    get_object_or_404(Todo, slug=slug).delete()
    return redirect('home')


def change_language(request):
    '''Handle language switching for unauthenticated users on the home page.'''
    if not request.user.is_authenticated:
        current_language = translation.get_language()
        user_language = request.POST.get('language')

        if user_language and user_language != current_language:
            translation.activate(user_language)
            homepage = reverse('home')
            response = HttpResponseRedirect(homepage)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
            return response

    return redirect('home')


@csrf_exempt
def sort(request):
    '''Handle sorting by updating an order field (of db elements).'''
    reordered = json.loads(request.POST.get('items'))

    if 'try' in request.META.get('HTTP_REFERER'):
        cookie_str = request.COOKIES.get('todo_list', '[]')
        todo_list = json.loads(cookie_str)
        indexes = [reordered[str(k)] for k in range(len(reordered))]
        todo_list_reordered = [
            item
            for idx, item in sorted(zip(indexes, todo_list), key=lambda i: i[0])
        ]
        response = HttpResponse(status=204)
        response.set_cookie('todo_list', json.dumps(todo_list_reordered))
        return response

    with transaction.atomic():
        for todo_id, todo_order in reordered.items():
            Todo.objects.filter(id=todo_id).update(order=todo_order)

    return HttpResponse(status=204)


def try_view(request):
    '''Give access to the main functionality to anonymous users.

    List of sample items is stored as a cookie that gets updated on change.
    '''
    the_page = reverse('try')

    if request.user.is_authenticated:
        return redirect('home')

    if not request.session or not request.session.session_key:
        request.session.save()
        todo_list = [
            {'text': _('Hello!'), 'is_done': False},
            {'text': _('Here you can try to add items'), 'is_done': False},
            {'text': _('Sort them the way you want'), 'is_done': False},
            {'text': _('Delete some of them'), 'is_done': True},
        ]
        response = HttpResponseRedirect(the_page)
        response.set_cookie('todo_list', json.dumps(todo_list))
        return response

    cookie_str = request.COOKIES.get('todo_list', '[]')
    todo_list = json.loads(cookie_str)

    form = TodoTryForm(request.POST or None)

    if form.is_valid():
        text = form.cleaned_data.get('text')
        todo_list.insert(0, {'text': text, 'is_done': False})
        response = HttpResponseRedirect(the_page)
        response.set_cookie('todo_list', json.dumps(todo_list))
        return response

    if request.method == 'POST':
        if 'is_done' in request.POST:
            item_index = request.POST.get('is_done')
            if 'unchecked' in item_index:
                item_index = int(item_index.split('-')[0])
                todo_list[item_index]['is_done'] = False
            else:
                todo_list[int(item_index)]['is_done'] = True
        elif 'delete' in request.POST:
            to_delete = int(request.POST.get('delete'))
            todo_list.pop(to_delete)

        response = HttpResponseRedirect(the_page)
        response.set_cookie('todo_list', json.dumps(todo_list))
        return response

    context = {'form': form, 'todo_list': todo_list}
    return render(request, 'try.html', context)


@api_view()
def serialized_items_view(request):
    """See how it turns out."""
    if not request.user.is_authenticated:
        return redirect('login')

    todos = Todo.objects.filter(owner=request.user)
    serializer = TodoSerializer(todos, many=True)
    return Response(serializer.data)
