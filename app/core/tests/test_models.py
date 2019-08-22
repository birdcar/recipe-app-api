from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@example.com", password="testpass"):
    """
    Create sample user for testing
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Creating a new user with an email should succeed"""
        email = "test@example.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Email addresses should be normalized"""
        email = "test@EXAMPLE.com"
        user = get_user_model().objects.create_user(email, 'testpass123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Users should always have a valid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Creating a superuser should work as expected"""
        user = get_user_model().objects.create_superuser(
            'test@superuseremail.com',
            'TestPass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_dunder_str(self):
        """
        The __str__ method for Tags should be properly implemented
        """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Charcuterie'
        )

        self.assertEqual(str(tag), tag.name)
