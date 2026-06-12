from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Character, CharacterGroup, Tag
from .permissions import IsOwner
from .services import duplicate_character
from .serializers import (
    CharacterDetailSerializer,
    CharacterGroupSerializer,
    CharacterListSerializer,
    CharacterTagsSerializer,
    CharacterTraitsBulkSerializer,
    TagSerializer,
)


class CharacterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        queryset = Character.objects.filter(owner=self.request.user).select_related(
            "line", "clan", "nature", "demeanor"
        )
        if self.action == "list":
            queryset = queryset.prefetch_related("tags")
            params = self.request.query_params
            line = params.get("line")
            if line:
                queryset = queryset.filter(line__code=line)
            tag = params.get("tag")
            if tag:
                queryset = queryset.filter(tags__name=tag)
            group = params.get("group")
            if group:
                queryset = queryset.filter(groups__id=group)
            search = params.get("search")
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search)
                    | Q(concept__icontains=search)
                    | Q(chronicle__icontains=search)
                )
            queryset = queryset.distinct()
        else:
            queryset = queryset.prefetch_related("traits__trait", "tags")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CharacterListSerializer
        return CharacterDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["put"], url_path="traits")
    def traits(self, request, pk=None):
        """Bulk-апсерт точек трейтов: повторный вызов обновляет, не плодит строки."""
        character = self.get_object()
        serializer = CharacterTraitsBulkSerializer(
            data=request.data, context={"character": character}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["post"], url_path="tags")
    def tags(self, request, pk=None):
        """Присвоить/снять теги: {"add": [id, ...], "remove": [id, ...]}."""
        character = self.get_object()
        serializer = CharacterTagsSerializer(
            data=request.data, context={"request": request, "character": character}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(self.get_object()).data)

    @action(detail=True, methods=["post"])
    def copy(self, request, pk=None):
        """Дубликат персонажа себе (вместе с трейтами, меритами и флоу)."""
        clone = duplicate_character(self.get_object(), owner=request.user)
        data = self.get_serializer(self.get_queryset().get(pk=clone.pk)).data
        return Response(data, status=status.HTTP_201_CREATED)


class OwnedModelViewSet(viewsets.ModelViewSet):
    """CRUD только по объектам владельца: чужие id дают 404."""

    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TagViewSet(OwnedModelViewSet):
    queryset = Tag.objects.prefetch_related("characters")
    serializer_class = TagSerializer


class CharacterGroupViewSet(OwnedModelViewSet):
    queryset = CharacterGroup.objects.prefetch_related("members")
    serializer_class = CharacterGroupSerializer
