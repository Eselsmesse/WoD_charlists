from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Регистрация по email + password. Токены выдаёт /auth/token/."""

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)


class MeView(generics.RetrieveAPIView):
    """Текущий аутентифицированный пользователь."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
