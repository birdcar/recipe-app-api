from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    """
    Views related to the Tag resource
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        """
        Return tags for the current authenticated user only
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Create a new Tag
        """
        serializer.save(user=self.request.user)


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Views related to the Ingredient resource
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        """
        Return Ingredients for the currently authenticated user only
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')
