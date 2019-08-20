from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """
    An endpoint to create a new user
    """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """
    An endpoint to create a new auth token for existing users
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
