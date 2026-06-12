from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from rules.models import Clan, GameLine, Trait

from .models import Character, CharacterTrait, Tag

User = get_user_model()


class CharacterModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="owner@example.com", password="StrongPass123")
        cls.line = GameLine.objects.create(code="vampire", name="Vampire: The Masquerade")
        cls.strength = Trait.objects.create(
            line=cls.line, category=Trait.Category.ATTRIBUTE, code="strength", name="Сила"
        )
        cls.celerity = Trait.objects.create(
            line=cls.line, category=Trait.Category.DISCIPLINE, code="celerity", name="Стремительность"
        )
        cls.clan = Clan.objects.create(line=cls.line, code="gangrel", name="Гангрел")

    def _make_character(self, name="Тестовый"):
        return Character.objects.create(owner=self.user, line=self.line, name=name)

    def test_create_character_with_traits(self):
        character = self._make_character()
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=3)
        CharacterTrait.objects.create(character=character, trait=self.celerity, rating=2)
        self.assertEqual(character.traits.count(), 2)

    def test_character_trait_unique_per_character(self):
        character = self._make_character()
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=3)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CharacterTrait.objects.create(character=character, trait=self.strength, rating=4)

    def test_owner_required(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Character.objects.create(owner=None, line=self.line, name="Без владельца")

    def test_line_protected_from_delete(self):
        self._make_character()
        with self.assertRaises(ProtectedError):
            self.line.delete()

    def test_used_trait_protected_from_delete(self):
        character = self._make_character()
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=1)
        with self.assertRaises(ProtectedError):
            self.strength.delete()

    def test_clan_delete_sets_null(self):
        character = self._make_character()
        character.clan = self.clan
        character.save()
        self.clan.delete()
        character.refresh_from_db()
        self.assertIsNone(character.clan)

    def test_character_delete_cascades_traits(self):
        character = self._make_character()
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=1)
        character.delete()
        self.assertEqual(CharacterTrait.objects.count(), 0)


class TagModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="tags@example.com", password="StrongPass123")
        cls.other = User.objects.create_user(email="other@example.com", password="StrongPass123")

    def test_tag_unique_per_owner(self):
        Tag.objects.create(owner=self.user, name="хроника-спб")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(owner=self.user, name="хроника-спб")

    def test_same_tag_name_for_different_owners(self):
        Tag.objects.create(owner=self.user, name="хроника-спб")
        Tag.objects.create(owner=self.other, name="хроника-спб")
        self.assertEqual(Tag.objects.filter(name="хроника-спб").count(), 2)
