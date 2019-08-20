from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTests(TestCase):
    """
    Test public (unauthenticated) requests to the user endpoints
    """

    def setUp(self):
        self.client = APIClient()
        self.good_user_obj = {
            'name': 'Testy McTest',
            'email': 'test@example.com',
            'password': 'testpass'
        }
        self.bad_user_password_obj = {
            'email': 'test@example.com',
            'password': 'pw'
        }

    def test_create_valid_user_success(self):
        """
        User should be created when valid payload is provided
        """
        res = self.client.post(CREATE_USER_URL, self.good_user_obj)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(self.good_user_obj['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user_failure(self):
        """
        User creation should fail when duplicate user exists
        """
        create_user(**self.good_user_obj)
        res = self.client.post(CREATE_USER_URL, self.good_user_obj)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length_failure(self):
        """
        User creation should fail when a password of insufficient length is
        provided
        """
        res = self.client.post(CREATE_USER_URL, self.bad_user_password_obj)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=self.bad_user_password_obj['email'])
        self.assertFalse(user_exists)
