from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Habit


class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("habit_creator",)

    def validate(self, attrs):
        # Создаем временный объект модели для проверки
        # (он не сохранится в базу, просто проверит данные)
        instance = Habit(**attrs)

        try:
            # Запускаем твою мощную валидацию из модели
            instance.clean()
        except DjangoValidationError as e:
            # Превращаем ошибку Django в ошибку DRF (400 код)
            raise serializers.ValidationError(
                e.message_dict if hasattr(e, 'message_dict') else e.messages
            )

        return attrs
