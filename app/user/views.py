from rest_framework import generics

from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    An endpoint to create a new user
    """
    serializer_class = UserSerializer
