from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    text = forms.CharField(
        label='',
        widget=forms.TextInput(),
    )

    class Meta:
        model = Todo
        fields = ['text']


class TodoTestForm(forms.Form):
    text = forms.CharField(
        label='',
        widget=forms.TextInput(),
    )
