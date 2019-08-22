from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
    Test unauthenticated requests made to the Tags resource
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Verify that authentication is required to retrieve Tags
        """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Test authenticated requests made to the Tags resource
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass',
            name='Testy McTester'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_tags_success(self):
        """
        User is able to retrieve tags
        """
        Tag.objects.create(user=self.user, name='Charcuterie')
        Tag.objects.create(user=self.user, name='Thai')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_tags_limited_to_user_success(self):
        """
        User can only retireve tags associated with their account
        """
        private_user = get_user_model().objects.create_user(
            name="Shawna Jean",
            email="shawna@leavemealone.com",
            password="mypasswordkeepsalltheboysfrommyyard"
        )
        Tags.objects.create(user=private_user, name="Southern")
        tag = Tags.objects.create(user=self.user, name="Seafood")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
