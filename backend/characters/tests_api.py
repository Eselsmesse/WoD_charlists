from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from rules.models import Archetype, Clan, GameLine, Trait

from .models import Character, CharacterTrait, Tag

User = get_user_model()


class CharactersApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(email="owner@example.com", password="StrongPass123")
        cls.stranger = User.objects.create_user(
            email="stranger@example.com", password="StrongPass123"
        )
        cls.line = GameLine.objects.create(code="vampire", name="Vampire: The Masquerade")
        cls.other_line = GameLine.objects.create(code="werewolf", name="Werewolf: The Apocalypse")
        cls.clan = Clan.objects.create(line=cls.line, code="ventrue", name="Вентру")
        cls.nature = Archetype.objects.create(line=cls.line, code="director", name="Руководитель")
        cls.strength = Trait.objects.create(
            line=cls.line, category=Trait.Category.ATTRIBUTE, code="strength", name="Сила",
            min_rating=1,
        )
        cls.brawl = Trait.objects.create(
            line=cls.line, category=Trait.Category.TALENT, code="brawl", name="Драка"
        )

    def auth(self, user=None):
        self.client.force_authenticate(user or self.owner)

    def make_character(self, owner=None, name="Мариус", **kwargs):
        return Character.objects.create(
            owner=owner or self.owner, line=self.line, name=name, **kwargs
        )


class CharacterCrudTests(CharactersApiTestCase):
    def test_create_character_with_codes(self):
        self.auth()
        response = self.client.post(
            "/api/v1/characters/",
            {
                "line": "vampire",
                "name": "Мариус",
                "clan": "ventrue",
                "nature": "director",
                "generation": 12,
                "owner": self.stranger.pk,  # должно игнорироваться
            },
        )
        self.assertEqual(response.status_code, 201, response.content)
        character = Character.objects.get(pk=response.json()["id"])
        self.assertEqual(character.owner, self.owner)
        self.assertEqual(character.clan, self.clan)
        self.assertEqual(character.generation, 12)

    def test_create_clan_from_wrong_line_rejected(self):
        self.auth()
        Clan.objects.create(line=self.other_line, code="get-of-fenris", name="Фенрис")
        response = self.client.post(
            "/api/v1/characters/",
            {"line": "vampire", "name": "Тест", "clan": "get-of-fenris"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("clan", response.json())

    def test_list_is_light_detail_is_full(self):
        self.auth()
        character = self.make_character()
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=3)

        list_data = self.client.get("/api/v1/characters/").json()
        self.assertEqual(list_data["count"], 1)
        self.assertNotIn("traits", list_data["results"][0])

        detail_data = self.client.get(f"/api/v1/characters/{character.pk}/").json()
        self.assertEqual(len(detail_data["traits"]), 1)
        self.assertEqual(detail_data["traits"][0]["trait"], "strength")

    def test_patch_and_delete(self):
        self.auth()
        character = self.make_character()
        response = self.client.patch(
            f"/api/v1/characters/{character.pk}/", {"concept": "Принц подполья"}
        )
        self.assertEqual(response.status_code, 200)
        character.refresh_from_db()
        self.assertEqual(character.concept, "Принц подполья")

        response = self.client.delete(f"/api/v1/characters/{character.pk}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Character.objects.filter(pk=character.pk).exists())

    def test_foreign_character_returns_404(self):
        self.auth(self.stranger)
        character = self.make_character()
        for method, url, payload in (
            ("get", f"/api/v1/characters/{character.pk}/", None),
            ("patch", f"/api/v1/characters/{character.pk}/", {"name": "x"}),
            ("delete", f"/api/v1/characters/{character.pk}/", None),
        ):
            response = getattr(self.client, method)(url, payload)
            self.assertEqual(response.status_code, 404, method)

    def test_unauthenticated_401(self):
        response = self.client.get("/api/v1/characters/")
        self.assertEqual(response.status_code, 401)


class CharacterFilterTests(CharactersApiTestCase):
    def test_filters(self):
        self.auth()
        marius = self.make_character(name="Мариус", chronicle="Москва")
        anna = self.make_character(name="Анна")
        tag = Tag.objects.create(owner=self.owner, name="спб")
        tag.characters.add(anna)

        data = self.client.get("/api/v1/characters/?search=Мариус").json()
        self.assertEqual([c["name"] for c in data["results"]], ["Мариус"])

        data = self.client.get("/api/v1/characters/?tag=спб").json()
        self.assertEqual([c["name"] for c in data["results"]], ["Анна"])

        data = self.client.get("/api/v1/characters/?line=vampire").json()
        self.assertEqual(data["count"], 2)

        data = self.client.get("/api/v1/characters/?line=werewolf").json()
        self.assertEqual(data["count"], 0)


class TraitBulkUpsertTests(CharactersApiTestCase):
    def url(self, character):
        return f"/api/v1/characters/{character.pk}/traits/"

    def test_upsert_creates_and_updates_without_duplicates(self):
        self.auth()
        character = self.make_character()
        payload = {"traits": [
            {"trait": "strength", "rating": 3, "specialty": "Удар"},
            {"trait": "brawl", "rating": 2},
        ]}
        response = self.client.put(self.url(character), payload, format="json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(character.traits.count(), 2)

        payload["traits"][0]["rating"] = 4
        response = self.client.put(self.url(character), payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(character.traits.count(), 2)
        self.assertEqual(character.traits.get(trait=self.strength).rating, 4)

    def test_unknown_trait_code_400(self):
        self.auth()
        character = self.make_character()
        response = self.client.put(
            self.url(character),
            {"traits": [{"trait": "no-such-trait", "rating": 1}]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("no-such-trait", str(response.json()))
        self.assertEqual(character.traits.count(), 0)

    def test_rating_above_max_400(self):
        self.auth()
        character = self.make_character()
        response = self.client.put(
            self.url(character),
            {"traits": [{"trait": "strength", "rating": 6}]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_foreign_character_404(self):
        self.auth(self.stranger)
        character = self.make_character()
        response = self.client.put(
            self.url(character),
            {"traits": [{"trait": "strength", "rating": 2}]},
            format="json",
        )
        self.assertEqual(response.status_code, 404)


class CharacterCopyTests(CharactersApiTestCase):
    def test_copy_duplicates_character_and_traits(self):
        self.auth()
        character = self.make_character(concept="Боксёр")
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=3)

        response = self.client.post(f"/api/v1/characters/{character.pk}/copy/")
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertNotEqual(data["id"], character.pk)
        self.assertEqual(data["name"], "Мариус (копия)")
        self.assertEqual(data["concept"], "Боксёр")
        self.assertEqual(len(data["traits"]), 1)

        clone = Character.objects.get(pk=data["id"])
        self.assertEqual(clone.owner, self.owner)
        self.assertEqual(clone.traits.get().rating, 3)
