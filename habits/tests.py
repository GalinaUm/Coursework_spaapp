from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from habits.models import Habit
from unittest.mock import patch
from django.utils import timezone
from habits.tasks import check_habits_and_notify

User = get_user_model()


class HabitTestCase(APITestCase):

    def setUp(self):
        # Используем create_user, чтобы пароль захешировался и логин работал
        self.user = User.objects.create_user(
            email="admin@sky.pro",
            password="0987654321admin"
        )

        # Создаем второго пользователя для теста прав доступа
        self.other_user = User.objects.create_user(
            email="other@sky.pro",
            password="password123"
        )

        # Принудительная авторизация под первым пользователем
        self.client.force_authenticate(user=self.user)

        # Создаем привычку первого пользователя
        self.habit = Habit.objects.create(
            habit_creator=self.user,
            habit="Моя привычка",
            time="10:00:00",
            periodicity=1
        )
        self.related_habit = Habit.objects.create(
            habit_creator=self.user,
            habit="Чай",
            time="10:00:00",
            is_pleasant=True
        )

    def test_other_user_habit_access(self):
        """Тест: пользователь не видит чужие привычки в своем списке"""
        # Создаем привычку ВТОРОГО пользователя
        Habit.objects.create(
            habit_creator=self.other_user,
            habit="Чужая привычка",
            time="12:00:00",
            periodicity=1
        )

        response = self.client.get(reverse("habits:habits-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        result_list = data.get('results') if isinstance(data, dict) else data

        self.assertEqual(len(result_list), 2)
        self.assertNotContains(response, "Чужая привычка")

    def test_delete_other_user_habit(self):
        """Тест: нельзя удалить чужую привычку"""
        other_habit = Habit.objects.create(
            habit_creator=self.other_user,
            habit="Удали меня если сможешь",
            time="15:00:00"
        )

        url = reverse("habits:habits-detail", args=[other_habit.id])
        response = self.client.delete(url)

        # Ожидаем 404 (так как get_queryset скрывает чужие объекты)
        # или 403 (если сработал IsOwner)
        self.assertTrue(
            response.status_code == status.HTTP_404_NOT_FOUND or
            response.status_code == status.HTTP_403_FORBIDDEN
        )

    def test_related_habit_no_reward(self):
        data = {
            "habit": "Приятная с ошибкой",
            "time": "10:00:00",
            "is_pleasant": True,
            "reward": "Шоколадка"  # Ошибка тут
        }
        response = self.client.post(reverse("habits:habits-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_habit_no_related(self):
        data = {
            "habit": "Приятная с ошибкой 2",
            "time": "10:00:00",
            "is_pleasant": True,
            "related_habit": self.related_habit.id  # Ошибка тут
        }
        response = self.client.post(reverse("habits:habits-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_related_must_be_pleasant(self):
        # Создаем обычную полезную привычку
        useful_habit = Habit.objects.create(
            habit_creator=self.user,
            habit="Бег",
            time="07:00:00"
        )
        data = {
            "habit": "Новая привычка",
            "time": "08:00:00",
            "related_habit": useful_habit.id  # Ошибка: она не приятная
        }
        response = self.client.post(reverse("habits:habits-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_habit_str(self):
        habit = Habit.objects.create(
            habit_creator=self.user,
            habit="Тест строки",
            time="10:00:00",
            place="Офис"
        )
        expected_str = f"{self.user.email} будет делать Тест строки в 10:00:00 в Офис"
        self.assertEqual(str(habit), expected_str)

    def test_public_habits_list(self):
        """Тест: публичные привычки видны всем"""
        # Создаем публичную привычку (другого пользователя)
        Habit.objects.create(
            habit_creator=self.other_user,
            habit="Публичная",
            time="10:00:00",
            is_public=True
        )

        # Вызываем именно этот экшн: /habits/public_list/
        url = reverse("habits:habits-public-list")  # Имя зависит от роутера
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в списке есть хотя бы одна привычка
        data = response.json()
        result_list = data.get('results', data)
        self.assertTrue(len(result_list) >= 1)





# ... внутри твоего класса HabitTestCase ...

@patch('habits.tasks.send_telegram_message')
def test_celery_task_sends_message(self, mock_send):
    """Тест: Celery-задача находит привычку и отправляет уведомление"""

    # 1. Берем текущее время (без секунд)
    now = timezone.now().time().replace(second=0, microsecond=0)

    # 2. Создаем привычку именно на ЭТО время
    habit = Habit.objects.create(
        habit_creator=self.user,
        habit="Тестовая задача",
        time=now,
        place="Офис"
    )

    # Убедимся, что у пользователя есть telegram_id
    self.user.telegram_id = "123456789"
    self.user.save()

    # 3. Запускаем задачу вручную
    # (В коде задачи проверь: habit.habit_creator.telegram_id вместо telegram_handle)
    check_habits_and_notify()

    # 4. Проверяем, была ли вызвана функция отправки
    mock_send.assert_called_once()

    # Проверяем, что в функцию ушли правильные данные
    args, kwargs = mock_send.call_args
    self.assertEqual(args[0], "123456789")
    self.assertIn("Тестовая задача", args[1])


def test_update_other_user_habit(self):
    """Тест: нельзя изменить чужую привычку"""
    other_habit = Habit.objects.create(
        habit_creator=self.other_user,
        habit="Чужая привычка",
        time="12:00:00"
    )
    url = reverse("habits:habits-detail", args=[other_habit.id])
    data = {"habit": "Я её взломал"}

    response = self.client.patch(url, data=data)

    # В твоем случае вернется 404, так как get_queryset её даже не найдет
    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


def test_public_list_filter(self):
    """Тест: в публичном списке только публичные привычки"""
    # Создаем одну публичную и одну приватную привычку (у другого юзера)
    Habit.objects.create(habit_creator=self.other_user, habit="Публичная",
                         time="10:00:00", is_public=True)
    Habit.objects.create(habit_creator=self.other_user, habit="Приватная",
                         time="11:00:00", is_public=False)

    url = reverse("habits:habits-public-list")
    response = self.client.get(url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Проверяем, что в ответе есть "Публичная", но нет "Приватная"
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
    # Создаем еще 10 привычек (всего будет 11 с той, что в setUp)
    for i in range(10):
        Habit.objects.create(habit_creator=self.user, habit=f"Привычка {i}", time="10:00:00")

    response = self.client.get(reverse("habits:habits-list"))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Проверяем, что в 'results' ровно 5 записей
    self.assertEqual(len(response.json()['results']), 5)
    # И что есть ссылка на следующую страницу
    self.assertIsNotNone(response.json()['next'])
