from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.tasks import check_habits_and_notify

User = get_user_model()


class HabitTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@sky.pro", password="0987654321admin"
        )

        self.other_user = User.objects.create_user(
            email="other@sky.pro", password="password123"
        )

        self.client.force_authenticate(user=self.user)

        self.habit = Habit.objects.create(
            habit_creator=self.user,
            habit="Моя привычка",
            time="10:00:00",
            periodicity=1,
        )
        self.related_habit = Habit.objects.create(
            habit_creator=self.user, habit="Чай", time="10:00:00", is_pleasant=True
        )

    def test_other_user_habit_access(self):
        """Тест: пользователь не видит чужие привычки в своем списке"""
        Habit.objects.create(
            habit_creator=self.other_user,
            habit="Чужая привычка",
            time="12:00:00",
            periodicity=1,
        )

        response = self.client.get(reverse("habits:habits-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        result_list = data.get("results") if isinstance(data, dict) else data

        self.assertEqual(len(result_list), 2)
        self.assertNotContains(response, "Чужая привычка")

    def test_delete_other_user_habit(self):
        """Тест: нельзя удалить чужую привычку"""
        other_habit = Habit.objects.create(
            habit_creator=self.other_user,
            habit="Удали меня если сможешь",
            time="15:00:00",
        )

        url = reverse("habits:habits-detail", args=[other_habit.id])
        response = self.client.delete(url)

        self.assertTrue(
            response.status_code == status.HTTP_404_NOT_FOUND
            or response.status_code == status.HTTP_403_FORBIDDEN
        )

    def test_related_habit_no_reward(self):
        data = {
            "habit": "Приятная с ошибкой",
            "time": "10:00:00",
            "is_pleasant": True,
            "reward": "Шоколадка",  # Ошибка тут
        }
        response = self.client.post(reverse("habits:habits-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_habit_no_related(self):
        data = {
            "habit": "Приятная с ошибкой 2",
            "time": "10:00:00",
            "is_pleasant": True,
            "related_habit": self.related_habit.id,
        }
        response = self.client.post(reverse("habits:habits-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_must_be_pleasant(self):
        useful_habit = Habit.objects.create(
            habit_creator=self.user, habit="Бег", time="07:00:00"
        )
        data = {
            "habit": "Новая привычка",
            "time": "08:00:00",
            "related_habit": useful_habit.id,
        }
        response = self.client.post(reverse("habits:habits-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_str(self):
        habit = Habit.objects.create(
            habit_creator=self.user, habit="Тест строки", time="10:00:00", place="Офис"
        )
        expected_str = f"{self.user.email} будет делать Тест строки в 10:00:00 в Офис"
        self.assertEqual(str(habit), expected_str)

    def test_public_habits_list(self):
        """Тест: публичные привычки видны всем"""
        Habit.objects.create(
            habit_creator=self.other_user,
            habit="Публичная",
            time="10:00:00",
            is_public=True,
        )

        url = reverse("habits:habits-public-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        result_list = data.get("results", data)
        self.assertTrue(len(result_list) >= 1)


@patch("habits.tasks.send_telegram_message")
def test_celery_task_sends_message(self, mock_send):
    """Тест: Celery-задача находит привычку и отправляет уведомление"""

    now = timezone.now().time().replace(second=0, microsecond=0)

    habit = Habit.objects.create(
        habit_creator=self.user, habit="Тестовая задача", time=now, place="Офис"
    )

    self.user.telegram_id = "123456789"
    self.user.save()

    check_habits_and_notify()

    mock_send.assert_called_once()

    args, kwargs = mock_send.call_args
    self.assertEqual(args[0], "123456789")
    self.assertIn("Тестовая задача", args[1])


def test_update_other_user_habit(self):
    """Тест: нельзя изменить чужую привычку"""
    other_habit = Habit.objects.create(
        habit_creator=self.other_user, habit="Чужая привычка", time="12:00:00"
    )
    url = reverse("habits:habits-detail", args=[other_habit.id])
    data = {"habit": "Я её взломал"}

    response = self.client.patch(url, data=data)

    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


def test_public_list_filter(self):
    """Тест: в публичном списке только публичные привычки"""
    Habit.objects.create(
        habit_creator=self.other_user,
        habit="Публичная",
        time="10:00:00",
        is_public=True,
    )
    Habit.objects.create(
        habit_creator=self.other_user,
        habit="Приватная",
        time="11:00:00",
        is_public=False,
    )

    url = reverse("habits:habits-public-list")
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertContains(response, "Публичная")
    self.assertNotContains(response, "Приватная")


def test_perform_create_sets_author(self):
    """Тест: создатель привычки ставится автоматически"""
    data = {
        "habit": "Авто-автор",
        "time": "15:00:00",
    }
    response = self.client.post(reverse("habits:habits-list"), data=data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    habit = Habit.objects.get(habit="Авто-автор")
    self.assertEqual(habit.habit_creator, self.user)


def test_pagination_works(self):
    """Тест: пагинация выдает по 5 объектов"""
    for i in range(10):
        Habit.objects.create(
            habit_creator=self.user, habit=f"Привычка {i}", time="10:00:00"
        )

    response = self.client.get(reverse("habits:habits-list"))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.json()["results"]), 5)
    self.assertIsNotNone(response.json()["next"])
