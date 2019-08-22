from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """
    Test unauthenticated requests made to the Ingredients resource
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Authentication is required for all actions associated with Ingredients
        """
        res = self.client.get(INGREDIENTS_URL)

        self.assertTrue(status.is_client_error(res.status_code))


class PrivateIngredientsApiTests(TestCase):
    """
    Test authenticated requests made to the Ingredients resourse
    """

    def setUp(self):
        # Configure and authenticate test user
        self.user = get_user_model().objects.create(
            name='Testy McTester',
            email='test@example.com',
            password='testpass'
        )
        self.private_user = get_user_model().objects.create_user(
            name="Shawna Jean",
            email="shawna@leavemealone.com",
            password="mypasswordkeepsalltheboysfrommyyard"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

        # Create Known Good (KG) and Known Bad (KB) payloads
        self.payload_KG = {
            'name': 'Salami'
        }
        self.payload_KB_name = {
            'name': ''
        }

    def test_get_ingredients_success(self):
        """
        User is able to retrieve ingredients
        """
        # Create two test ingredients
        Ingredient.objects.create(
            user=self.user,
            name='Swiss Chard'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Salt'
        )

        # Make request for ingredients through client
        res = self.client.get(INGREDIENTS_URL)

        # Get serialized data from database for comparison
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        # Assert that request is successful and data matches
        self.assertTrue(status.is_success(res.status_code))
        self.assertEqual(res.data, serializer.data)

    def test_get_ingredients_limited_to_user_success(self):
        """
        User can only retrieve ingredients associated with their account
        """
        Ingredient.objects.create(
            user=self.private_user,
            name='Chocolate Chips'
        )
        my_ingredient = Ingredient.objects.create(
            user=self.user,
            name="Onions"
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertTrue(status.is_success(res.status_code))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], my_ingredient.name)

    def test_ingredient_create_success(self):
        """
        User is able to create new ingredients
        """
        res = self.client.post(INGREDIENTS_URL, self.payload_KG)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=self.payload_KG['name']
        ).exists()

        self.assertTrue(status.is_success(res.status_code))
        self.assertTrue(exists)

    def test_ingredient_missing_name_create_failure(self):
        """
        User cannot create new ingredients without a name
        """
        res = self.client.post(INGREDIENTS_URL, self.payload_KB_name)

        self.assertTrue(status.is_client_error(res.status_code))
