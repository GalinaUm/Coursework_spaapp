from django.urls import path
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.views import (UserCreateAPIView, UserDestroyAPIView,
                         UserListAPIView, UserRetrieveAPIView,
                         UserUpdateAPIView)

app_name = UsersConfig.name
urlpatterns = [
    path("", UserListAPIView.as_view(permission_classes = [IsAdminUser]), name="users_list"),
    path("create/", UserCreateAPIView.as_view(), name="user_create"),
    path("update/<int:pk>/", UserUpdateAPIView.as_view(), name="user_update"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user_get"),
    path("delete/<int:pk>/", UserDestroyAPIView.as_view(), name="user_delete"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=[AllowAny]),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=[AllowAny]),
        name="token_refresh",
    ),
]
