from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Habit

class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('habit_creator',)

    def validate_(self, attrs):
        """
        Дополнительная проверка на уровне API.
        """
        duration = attrs.get('duration')
        if duration and duration > 120:
            raise serializers.ValidationError(
                {"duration": "Время выполнения не может превышать 120 секунд."}
            )
        return attrs