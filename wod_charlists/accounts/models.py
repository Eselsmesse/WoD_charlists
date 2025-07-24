from django.db import models

class GoogleUser(models.Model):
    """Пользователь, прошедший авторизацию через Google."""
    google_id = models.CharField(max_length=50, unique=True, verbose_name="Google ID")
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=150, blank=True, verbose_name="Name")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Google User"
        verbose_name_plural = "Google Users"

    def __str__(self):
        return self.email
