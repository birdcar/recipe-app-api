from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """
    Generate a new Recipe object and return it
    """
    default = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    default.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(self):
    """
    Test unauthenticated requests made to the Recipe resource
    """

    def setUp(self):
        self.client = APIClient

    def test_require_auth(self):
        """
        Authentication is required for all actions associated with Recipes
        """
        res = self.client.get(RECIPE_URL)

        self.assertTrue(status.is_client_error(res.status_code))


class PrivateRecipeAPITests(self):
    """
    Test authenticated requests made to the Recipe resource
    """

    def setUp(self):
        self.client = APIClient
        self.user = get_user_model().objects.create_user(
            name="Testy McTester",
            email="test@example.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)
        self.private_user = get_user_model().objects.create_user(
            name="Shawna Jean",
            email="shawna@leavemealone.com",
            password="mypasswordkeepsalltheboysfrommyyard"
        )

        self.payload_KG = sample_recipe(self.user)
        self.payload_KB_missing_title = Recipe.objects.create(
            title='',
            time_minutes=10,
            price=5.00
        )

    def test_get_recipes_success(self):
        """
        Users are able to retrieve recipes
        """
        res = self.client.get(RECIPE_URL)

        self.assertTrue(status.is_success(res.status_code))
