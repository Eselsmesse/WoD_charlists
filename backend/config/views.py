"""Служебные вьюхи уровня проекта (health-check и т.п.)."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Заглушечный health-check каркаса API."""
    return Response({"status": "ok"})
