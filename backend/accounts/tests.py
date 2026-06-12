from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class HealthEndpointTests(APITestCase):
    def test_health_returns_ok(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class UserModelTests(APITestCase):
    def test_create_user_by_email(self):
        user = User.objects.create_user(email="test@example.com", password="StrongPass123")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("StrongPass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="StrongPass123")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="StrongPass123")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, "email")


class JwtTests(APITestCase):
    def test_jwt_pair_issued_for_user(self):
        user = User.objects.create_user(email="jwt@example.com", password="StrongPass123")
        refresh = RefreshToken.for_user(user)
        self.assertTrue(str(refresh))
        self.assertTrue(str(refresh.access_token))
