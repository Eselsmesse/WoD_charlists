from datetime import timedelta

from django.utils import timezone

from characters.models import Character, CharacterTrait
from characters.tests_api import CharactersApiTestCase

from .models import ShareLink


class SharingApiTestCase(CharactersApiTestCase):
    def make_shared(self, **link_kwargs):
        character = self.make_character(concept="Боксёр")
        CharacterTrait.objects.create(character=character, trait=self.strength, rating=3)
        link = ShareLink.objects.create(character=character, **link_kwargs)
        return character, link


class ShareLinkCreateRevokeTests(SharingApiTestCase):
    def test_owner_creates_link(self):
        self.auth()
        character = self.make_character()
        response = self.client.post(f"/api/v1/characters/{character.pk}/share/")
        self.assertEqual(response.status_code, 201, response.content)
        token = response.json()["token"]
        self.assertTrue(ShareLink.objects.filter(character=character, token=token).exists())

    def test_stranger_cannot_create_or_revoke(self):
        character = self.make_character()
        link = ShareLink.objects.create(character=character)
        self.auth(self.stranger)
        response = self.client.post(f"/api/v1/characters/{character.pk}/share/")
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(f"/api/v1/characters/{character.pk}/share/{link.token}/")
        self.assertEqual(response.status_code, 404)

    def test_owner_revokes_link(self):
        self.auth()
        character, link = self.make_shared()
        response = self.client.delete(f"/api/v1/characters/{character.pk}/share/{link.token}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(ShareLink.objects.filter(pk=link.pk).exists())
        # после отзыва публичная ссылка не работает
        self.assertEqual(self.client.get(f"/api/v1/shared/{link.token}/").status_code, 404)


class SharedPublicViewTests(SharingApiTestCase):
    def test_anonymous_reads_shared_character(self):
        character, link = self.make_shared()
        response = self.client.get(f"/api/v1/shared/{link.token}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Мариус")
        self.assertEqual(data["traits"][0]["trait"], "strength")

    def test_no_private_fields_leaked(self):
        character, link = self.make_shared()
        data = self.client.get(f"/api/v1/shared/{link.token}/").json()
        for private in ("owner", "player", "tags", "id", "is_public", "email"):
            self.assertNotIn(private, data)
        self.assertNotIn("owner@example.com", str(data))

    def test_invalid_token_404(self):
        response = self.client.get("/api/v1/shared/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(response.status_code, 404)

    def test_expired_token_404(self):
        character, link = self.make_shared(expires_at=timezone.now() - timedelta(hours=1))
        self.assertEqual(self.client.get(f"/api/v1/shared/{link.token}/").status_code, 404)

    def test_unexpired_token_ok(self):
        character, link = self.make_shared(expires_at=timezone.now() + timedelta(hours=1))
        self.assertEqual(self.client.get(f"/api/v1/shared/{link.token}/").status_code, 200)


class SharedCopyTests(SharingApiTestCase):
    def test_copy_to_other_user(self):
        character, link = self.make_shared()
        self.auth(self.stranger)
        response = self.client.post(f"/api/v1/shared/{link.token}/copy/")
        self.assertEqual(response.status_code, 201, response.content)
        clone = Character.objects.get(pk=response.json()["id"])
        self.assertEqual(clone.owner, self.stranger)
        self.assertEqual(clone.traits.get().rating, 3)
        self.assertNotEqual(clone.pk, character.pk)

    def test_copy_requires_auth(self):
        character, link = self.make_shared()
        response = self.client.post(f"/api/v1/shared/{link.token}/copy/")
        self.assertEqual(response.status_code, 401)

    def test_copy_forbidden_when_disabled(self):
        character, link = self.make_shared(can_copy=False)
        self.auth(self.stranger)
        response = self.client.post(f"/api/v1/shared/{link.token}/copy/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Character.objects.filter(owner=self.stranger).count(), 0)
