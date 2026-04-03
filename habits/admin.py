from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "habit_creator",
        "habit",
        "time",
        "is_pleasant",
        "periodicity",
    )
    list_filter = (
        "is_pleasant",
        "is_public",
        "habit_creator",
    )
    search_fields = (
        "habit",
        "place",
        "habit_creator__username",
    )
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("habit_creator", "habit", "place", "time", "duration")},
        ),
        (
            "Логика привычки",
            {"fields": ("is_pleasant", "related_habit", "reward", "periodicity")},
        ),
        ("Доступ", {"fields": ("is_public",)}),
    )
