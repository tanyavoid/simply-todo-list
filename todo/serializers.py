from rest_framework import serializers

from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = [
            'id',
            'owner',
            'text',
            'slug',
            'date_added',
            'date_done',
            'is_done',
            'order',
        ]
