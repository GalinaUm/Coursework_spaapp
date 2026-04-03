from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class UserTestCase(APITestCase):

    def test_user_registration(self):
        """Тест регистрации и хеширования пароля"""
        self.client.force_authenticate(user=None)
        data = {
            "email": "new@test.ru",
            "password": "mypassword123",
            "city": "Moscow"
        }
        response = self.client.post(reverse("users:user_create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="new@test.ru")
        self.assertTrue(user.check_password("mypassword123"))

    def test_login_jwt(self):
        """Тест получения токена"""
        User.objects.create_user(email="login@test.ru", password="password")
        data = {"email": "login@test.ru", "password": "password"}
        response = self.client.post(reverse("users:login"), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

    def test_user_list_forbidden_for_common(self):
        """Тест: обычный пользователь не видит список юзеров (IsAdminUser)"""
        user = User.objects.create_user(email="common@test.ru", password="123")
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("users:users_list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_allowed_for_staff(self):
        """Тест: админ видит список юзеров"""
        admin = User.objects.create_user(email="staff@test.ru", password="123", is_staff=True)
        self.client.force_authenticate(user=admin)

        response = self.client.get(reverse("users:users_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
