from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from characters.models import Character
from characters.serializers import CharacterDetailSerializer
from characters.services import duplicate_character

from .models import ShareLink
from .serializers import PublicCharacterSerializer, ShareLinkSerializer


def get_own_character_or_404(request, character_id):
    """Персонаж текущего пользователя; чужой/несуществующий id → 404."""
    return get_object_or_404(Character, pk=character_id, owner=request.user)


def get_active_link_or_404(token):
    return get_object_or_404(ShareLink.objects.active().select_related("character"), token=token)


class ShareLinkCreateView(APIView):
    """POST /characters/{id}/share/ — создать публичную ссылку (owner)."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, character_id):
        character = get_own_character_or_404(request, character_id)
        serializer = ShareLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = serializer.save(character=character)
        return Response(ShareLinkSerializer(link).data, status=status.HTTP_201_CREATED)


class ShareLinkRevokeView(APIView):
    """DELETE /characters/{id}/share/{token}/ — отозвать ссылку (owner)."""

    permission_classes = (IsAuthenticated,)

    def delete(self, request, character_id, token):
        character = get_own_character_or_404(request, character_id)
        link = get_object_or_404(ShareLink, character=character, token=token)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SharedCharacterView(APIView):
    """GET /shared/{token}/ — публичный read-only чарник по токену."""

    permission_classes = (AllowAny,)

    def get(self, request, token):
        link = get_active_link_or_404(token)
        return Response(PublicCharacterSerializer(link.character).data)


class SharedCharacterCopyView(APIView):
    """POST /shared/{token}/copy/ — сохранить копию себе (если can_copy)."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, token):
        link = get_active_link_or_404(token)
        if not link.can_copy:
            raise PermissionDenied("Владелец запретил копирование этого чарника.")
        clone = duplicate_character(link.character, owner=request.user)
        return Response(
            CharacterDetailSerializer(clone).data, status=status.HTTP_201_CREATED
        )
