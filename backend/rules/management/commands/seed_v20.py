"""Идемпотентная загрузка каталога V20 из rules/data/*.json.

Upsert по натуральным ключам: Trait — (line, category, code); Clan, Archetype,
CreationRule — (line, code/key); GenerationStat — (line, generation).
Повторный запуск обновляет записи, не создавая дублей. Поле origin при
обновлении не трогаем: проставленное владельцем "проверено" не сбрасывается.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from rules.models import Archetype, Clan, CreationRule, GameLine, GenerationStat, Trait

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load(filename):
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


class Command(BaseCommand):
    help = "Загружает (идемпотентно) каталог правил V20 из rules/data/*.json"

    @transaction.atomic
    def handle(self, *args, **options):
        counters = {}

        gameline = _load("v20_gameline.json")
        line, _ = GameLine.objects.update_or_create(
            code=gameline["code"],
            defaults={"name": gameline["name"], "edition": gameline["edition"]},
        )
        counters["GameLine"] = GameLine.objects.count()

        data = _load("v20_traits.json")
        for entry in data["traits"]:
            self._upsert(
                Trait,
                {"line": line, "category": entry["category"], "code": entry["code"]},
                {
                    "name": entry["name"],
                    "subgroup": entry.get("subgroup", ""),
                    "min_rating": entry.get("min_rating", 0),
                    "max_rating": entry.get("max_rating", 5),
                    "requires_specialty_at": entry.get("requires_specialty_at"),
                    "order": entry.get("order", 0),
                    "source": data["source"],
                },
            )
        counters["Trait"] = Trait.objects.filter(line=line).count()

        data = _load("v20_clans.json")
        for entry in data["clans"]:
            clan = self._upsert(
                Clan,
                {"line": line, "code": entry["code"]},
                {
                    "name": entry["name"],
                    "default_sect": entry.get("default_sect", ""),
                    "weakness_summary": entry.get("weakness_summary", ""),
                    "is_bloodline": entry.get("is_bloodline", False),
                    "source": data["source"],
                },
            )
            disciplines = Trait.objects.filter(
                line=line,
                category=Trait.Category.DISCIPLINE,
                code__in=entry["disciplines"],
            )
            if disciplines.count() != len(entry["disciplines"]):
                missing = set(entry["disciplines"]) - set(disciplines.values_list("code", flat=True))
                raise SystemExit(f"Клан {entry['code']}: нет дисциплин {missing} в каталоге")
            clan.disciplines.set(disciplines)
        counters["Clan"] = Clan.objects.filter(line=line).count()

        data = _load("v20_archetypes.json")
        for entry in data["archetypes"]:
            self._upsert(
                Archetype,
                {"line": line, "code": entry["code"]},
                {"name": entry["name"], "summary": entry.get("summary", ""), "source": data["source"]},
            )
        counters["Archetype"] = Archetype.objects.filter(line=line).count()

        data = _load("v20_generations.json")
        for entry in data["generations"]:
            self._upsert(
                GenerationStat,
                {"line": line, "generation": entry["generation"]},
                {
                    "max_blood_pool": entry["max_blood_pool"],
                    "blood_per_turn": entry["blood_per_turn"],
                    "max_trait_rating": entry["max_trait_rating"],
                    "source": data["source"],
                },
            )
        counters["GenerationStat"] = GenerationStat.objects.filter(line=line).count()

        data = _load("v20_creation_rules.json")
        for entry in data["rules"]:
            self._upsert(
                CreationRule,
                {"line": line, "key": entry["key"]},
                {
                    "value": entry["value"],
                    "description": entry.get("description", ""),
                    "source": data["source"],
                },
            )
        counters["CreationRule"] = CreationRule.objects.filter(line=line).count()

        if options.get("verbosity", 1) >= 1:
            for model, count in counters.items():
                self.stdout.write(self.style.SUCCESS(f"{model}: {count}"))

    @staticmethod
    def _upsert(model, keys, defaults):
        obj, created = model.objects.update_or_create(**keys, defaults=defaults)
        return obj
