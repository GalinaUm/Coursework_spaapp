from django.urls import path

from users.apps import UsersConfig
from users.views import UserListAPIView, UserCreateAPIView, UserUpdateAPIView, UserRetrieveAPIView, UserDestroyAPIView

app_name = UsersConfig.name
urlpatterns = [
    path("", UserListAPIView.as_view(), name="users_list"),
    path("create/", UserCreateAPIView.as_view(), name="user_create"),
    path("update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user_get"),
    path("delete/<int:pk>/", UserDestroyAPIView.as_view(), name="user_delete"),

]
