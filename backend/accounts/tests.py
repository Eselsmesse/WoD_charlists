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


class RegisterApiTests(APITestCase):
    url = "/api/v1/auth/register/"

    def test_register_success(self):
        response = self.client.post(
            self.url, {"email": "new@example.com", "password": "StrongPass123"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "new@example.com")
        self.assertNotIn("password", response.json())
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email="taken@example.com", password="StrongPass123")
        response = self.client.post(
            self.url, {"email": "taken@example.com", "password": "StrongPass123"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())

    def test_register_weak_password_rejected(self):
        response = self.client.post(self.url, {"email": "weak@example.com", "password": "123"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())
        self.assertFalse(User.objects.filter(email="weak@example.com").exists())


class TokenApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="login@example.com", password="StrongPass123")

    def test_token_obtain_pair(self):
        response = self.client.post(
            "/api/v1/auth/token/", {"email": "login@example.com", "password": "StrongPass123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_token_wrong_password(self):
        response = self.client.post(
            "/api/v1/auth/token/", {"email": "login@example.com", "password": "WrongPass999"}
        )
        self.assertEqual(response.status_code, 401)

    def test_token_refresh(self):
        pair = self.client.post(
            "/api/v1/auth/token/", {"email": "login@example.com", "password": "StrongPass123"}
        ).json()
        response = self.client.post("/api/v1/auth/token/refresh/", {"refresh": pair["refresh"]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())


class MeApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="me@example.com", password="StrongPass123", first_name="Имя"
        )

    def test_me_without_token(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_with_token(self):
        access = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "me@example.com")
        self.assertEqual(data["first_name"], "Имя")
        self.assertNotIn("password", data)
