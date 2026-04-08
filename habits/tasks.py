from datetime import datetime

from celery import shared_task

from users.services import send_telegram_message

from .models import Habit


@shared_task
def check_habits_and_notify():
    now_time = datetime.now().time().replace(second=0, microsecond=0)
    habits_to_remind = Habit.objects.filter(time=now_time)

    for habit in habits_to_remind:
        message = f"Напоминание: {habit.habit} в {habit.place}!"
        if habit.habit_creator.telegram_id:  # Если у юзера заполнен ID
            send_telegram_message(habit.habit_creator.telegram_id, message)
