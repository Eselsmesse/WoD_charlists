from django.core.management import call_command
from django.test import TestCase

from .models import Archetype, Clan, CreationRule, GameLine, GenerationStat, Trait


class SeedV20Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_v20", verbosity=0)

    def _counts(self):
        return {
            "lines": GameLine.objects.count(),
            "attributes": Trait.objects.filter(category=Trait.Category.ATTRIBUTE).count(),
            "abilities": Trait.objects.filter(
                category__in=[
                    Trait.Category.TALENT,
                    Trait.Category.SKILL,
                    Trait.Category.KNOWLEDGE,
                ]
            ).count(),
            "disciplines": Trait.objects.filter(category=Trait.Category.DISCIPLINE).count(),
            "backgrounds": Trait.objects.filter(category=Trait.Category.BACKGROUND).count(),
            "virtues": Trait.objects.filter(category=Trait.Category.VIRTUE).count(),
            "clans": Clan.objects.count(),
            "archetypes": Archetype.objects.count(),
            "generations": GenerationStat.objects.count(),
            "creation_rules": CreationRule.objects.count(),
        }

    def test_expected_counts(self):
        counts = self._counts()
        self.assertEqual(counts["lines"], 1)
        self.assertEqual(counts["attributes"], 9)
        self.assertEqual(counts["abilities"], 30)
        self.assertEqual(counts["disciplines"], 18)
        self.assertEqual(counts["backgrounds"], 12)
        self.assertEqual(counts["virtues"], 5)
        self.assertEqual(counts["clans"], 13)
        self.assertEqual(counts["archetypes"], 41)
        self.assertEqual(counts["generations"], 10)
        self.assertEqual(counts["creation_rules"], 12)

    def test_idempotent_rerun(self):
        before = self._counts()
        call_command("seed_v20", verbosity=0)
        self.assertEqual(self._counts(), before)

    def test_rerun_keeps_verified_origin(self):
        trait = Trait.objects.get(code="strength")
        trait.origin = Trait.Origin.VERIFIED
        trait.save()
        call_command("seed_v20", verbosity=0)
        trait.refresh_from_db()
        self.assertEqual(trait.origin, Trait.Origin.VERIFIED)

    def test_ventrue_clan_disciplines(self):
        ventrue = Clan.objects.get(code="ventrue")
        self.assertEqual(
            set(ventrue.disciplines.values_list("code", flat=True)),
            {"dominate", "fortitude", "presence"},
        )

    def test_clan_disciplines_have_three(self):
        for clan in Clan.objects.all():
            self.assertEqual(clan.disciplines.count(), 3, clan.code)

    def test_generation_13_stats(self):
        gen13 = GenerationStat.objects.get(generation=13)
        self.assertEqual(gen13.max_blood_pool, 10)
        self.assertEqual(gen13.blood_per_turn, 1)
        self.assertEqual(gen13.max_trait_rating, 5)

    def test_creation_rules_values(self):
        line = GameLine.objects.get(code="vampire")
        self.assertEqual(
            CreationRule.objects.get(line=line, key="attribute_priorities").value, [7, 5, 3]
        )
        self.assertEqual(CreationRule.objects.get(line=line, key="freebie_points").value, 15)
        costs = CreationRule.objects.get(line=line, key="freebie_costs").value
        self.assertEqual(costs["discipline"], 7)

    def test_all_records_marked_parsed_with_source(self):
        self.assertFalse(Trait.objects.filter(source="").exists())
        self.assertFalse(Clan.objects.filter(source="").exists())
        self.assertTrue(
            Trait.objects.filter(origin=Trait.Origin.PARSED).count() == Trait.objects.count()
        )
