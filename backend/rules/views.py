"""Read-only API справочника правил. Доступен без авторизации (AllowAny)."""

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GameLine, Trait
from .serializers import (
    ArchetypeSerializer,
    ClanSerializer,
    GameLineSerializer,
    TraitSerializer,
)


class LineListView(generics.ListAPIView):
    queryset = GameLine.objects.filter(is_active=True)
    serializer_class = GameLineSerializer
    permission_classes = (AllowAny,)


class LineDetailView(generics.RetrieveAPIView):
    queryset = GameLine.objects.filter(is_active=True)
    serializer_class = GameLineSerializer
    permission_classes = (AllowAny,)
    lookup_field = "code"


class LineScopedListView(generics.ListAPIView):
    """База для списков внутри линейки: /lines/{code}/<ресурс>/."""

    permission_classes = (AllowAny,)

    def get_line(self):
        return get_object_or_404(GameLine, code=self.kwargs["code"], is_active=True)


class TraitListView(LineScopedListView):
    serializer_class = TraitSerializer

    def get_queryset(self):
        queryset = Trait.objects.filter(line=self.get_line())
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        subgroup = self.request.query_params.get("subgroup")
        if subgroup:
            queryset = queryset.filter(subgroup=subgroup)
        return queryset


class ClanListView(LineScopedListView):
    serializer_class = ClanSerializer

    def get_queryset(self):
        return self.get_line().clans.prefetch_related("disciplines")


class ArchetypeListView(LineScopedListView):
    serializer_class = ArchetypeSerializer

    def get_queryset(self):
        return self.get_line().archetypes.all()


class CreationRulesView(APIView):
    """Числа создания персонажа и таблица поколений — из данных, не из кода."""

    permission_classes = (AllowAny,)

    def get(self, request, code):
        line = get_object_or_404(GameLine, code=code, is_active=True)
        rules = {rule.key: rule.value for rule in line.creation_rules.all()}
        generations = list(
            line.generation_stats.values(
                "generation", "max_blood_pool", "blood_per_turn", "max_trait_rating"
            )
        )
        return Response({"rules": rules, "generations": generations})
