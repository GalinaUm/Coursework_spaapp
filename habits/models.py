from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Habit(models.Model):
    habit_creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
    )
    habit = models.TextField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Полезная привычка",
        help_text = "Укажите полезную привычку"
    )
    place = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="Место выполнения",
        help_text="Укажите место, где вам пригодится эта привычка",
    )
    time = models.TimeField(
        verbose_name="Время выполнения",
        help_text="Укажите время, когда нужно выполнить привычку (например, 08:00)"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_habits',
        verbose_name="Связанная привычка",
        help_text="Сюда можно добавить только приятную привычку"
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность (в днях)",
        help_text="Как часто нужно напоминать о привычке",
    )
    reward = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Чем вы себя порадуете после выполнения (если нет связанной приятной привычки)"
    )
    duration = models.PositiveIntegerField(
        default=120,
        verbose_name="Время на выполнение (в секундах)",
        help_text="Не должно превышать 120 секунд"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Видна ли привычка другим пользователям"
    )

    def __str__(self):
        return f"{self.habit_creator} будет делать {self.habit} в {self.time} в {self.place}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def clean(self):
        if self.related_habit and self.reward:
            raise ValidationError(
                "Нельзя одновременно выбрать связанную привычку и вознаграждение."
            )
        if self.duration and self.duration > 120:
            raise ValidationError(
                {'duration': "Время выполнения должно быть не больше 120 секунд."}
            )
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                {'related_habit': "В связанные привычки можно добавлять только приятные привычки."}
            )
        if self.is_pleasant:
            if self.reward or self.related_habit:
                raise ValidationError(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )
        if self.periodicity and self.periodicity > 7:
            raise ValidationError(
                {'periodicity': "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)