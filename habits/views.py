from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsOwner

from .models import Habit
from .paginators import HabitPagination
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Если пользователь хочет редактировать или удалить (action: update, destroy)
        if self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Для просмотра списка или создания достаточно быть авторизованным
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """Список привычек текущего пользователя (для CRUD)"""
        # Если это не запрос к списку публичных привычек, фильтруем по владельцу
        if self.action == "public_list":
            return Habit.objects.filter(is_public=True)
        return Habit.objects.filter(habit_creator=self.request.user)

    def perform_create(self, serializer):
        """Привязываем новую привычку к текущему пользователю"""
        serializer.save(habit_creator=self.request.user)

    @action(detail=False, methods=["get"])
    def public_list(self, request):
        """Отдельный эндпоинт для публичных привычек: /habits/public_list/"""
        public_habits = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)
