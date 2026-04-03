from datetime import datetime
from celery import shared_task
from .models import Habit
from users.services import send_telegram_message


@shared_task
def check_habits_and_notify():
    now_time = datetime.now().time().replace(second=0, microsecond=0)
    # Ищем привычки, время которых совпало с текущим (с точностью до минуты)
    habits_to_remind = Habit.objects.filter(time=now_time)

    for habit in habits_to_remind:
        message = f"Напоминание: {habit.habit} в {habit.place}!"
        if habit.habit_creator.telegram_handle:  # Если у юзера заполнен ID
            send_telegram_message(habit.habit_creator.telegram_handle, message)
