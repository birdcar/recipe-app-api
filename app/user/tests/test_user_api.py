from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test public (unauthenticated) requests to the user endpoints
    """

    def setUp(self):
        self.client = APIClient()
        self.valid_user_new = {
            'name': 'Testy McTester',
            'email': 'test@example.com',
            'password': 'testpass'
        }
        self.valid_user_creds = {
            'email': 'test@example.com',
            'password': 'testpass'
        }
        self.invalid_user_password = {
            'email': 'test@example.com',
            'password': 'pw'
        }

    def test_create_valid_user_success(self):
        """
        User should be created when valid payload is provided
        """
        res = self.client.post(CREATE_USER_URL, self.valid_user_new)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(self.valid_user_new['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user_failure(self):
        """
        User creation should fail when duplicate user exists
        """
        create_user(**self.valid_user_new)
        res = self.client.post(CREATE_USER_URL, self.valid_user_new)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_length_failure(self):
        """
        User creation should fail when a password of insufficient length is
        provided
        """
        res = self.client.post(CREATE_USER_URL, self.invalid_user_password)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=self.invalid_user_password['email'])
        self.assertFalse(user_exists)

    def test_valid_user_token_creation(self):
        """
        A token should be created when a user provides valid credentials
        """
        create_user(**self.valid_user_new)
        res = self.client.post(TOKEN_URL, self.valid_user_creds)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_user_token_failure(self):
        """
        A token should not be created when a user provides invalid credentials
        """
        create_user(**self.valid_user_new)
        res = self.client.post(TOKEN_URL, self.invalid_user_password)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_token_failure(self):
        """
        A token should not be created or if a user does not exist
        """
        res = self.client.post(TOKEN_URL, self.valid_user_new)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_password_token_failure(self):
        res = self.client.post(
            TOKEN_URL, {'email': 'test@example.com', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_user_email_token_failure(self):
        res = self.client.post(
            TOKEN_URL, {'email': '', 'password': 'testpass'})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_profile_management_failure(self):
        """
        Authentication should be required to manage your user
        """
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test private (authenticated) requests to the API
    """

    def setUp(self):
        self.user = create_user(email='test@example.com',
                                password="testpass",
                                name="Testy McTester")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_provile_success(self):
        """
        A valid, authenticated user can retrieve their profile
        """
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': 'test@example.com',
            'name': 'Testy McTester'
        })

    def test_profile_post_failure(self):
        """
        The profile endpoint should not allow POST requests
        """
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_profile_patch_success(self):
        """
        A valid, authenticated user should be able to update their profile
        """
        updates = {'name': 'Not Testy McTester', 'password': 'newtestpass'}
        res = self.client.patch(PROFILE_URL, updates)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, updates['name'])
        self.assertTrue(self.user.check_password(updates['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
