from .models import CharacterGroup, Tag
from .tests_api import CharactersApiTestCase


class TagApiTests(CharactersApiTestCase):
    def test_tag_crud_and_owner_isolation(self):
        self.auth()
        response = self.client.post("/api/v1/tags/", {"name": "хроника-спб", "color": "#aa0000"})
        self.assertEqual(response.status_code, 201, response.content)
        tag_id = response.json()["id"]
        self.assertEqual(Tag.objects.get(pk=tag_id).owner, self.owner)

        response = self.client.patch(f"/api/v1/tags/{tag_id}/", {"name": "хроника-мск"})
        self.assertEqual(response.status_code, 200)

        # чужому пользователю тег не виден и недоступен
        self.auth(self.stranger)
        self.assertEqual(self.client.get("/api/v1/tags/").json()["count"], 0)
        self.assertEqual(self.client.get(f"/api/v1/tags/{tag_id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/v1/tags/{tag_id}/").status_code, 404)

        self.auth()
        self.assertEqual(self.client.delete(f"/api/v1/tags/{tag_id}/").status_code, 204)

    def test_duplicate_tag_name_400(self):
        self.auth()
        Tag.objects.create(owner=self.owner, name="спб")
        response = self.client.post("/api/v1/tags/", {"name": "спб"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json())

    def test_same_name_for_other_owner_ok(self):
        Tag.objects.create(owner=self.owner, name="спб")
        self.auth(self.stranger)
        response = self.client.post("/api/v1/tags/", {"name": "спб"})
        self.assertEqual(response.status_code, 201)

    def test_tag_cannot_include_foreign_character(self):
        self.auth()
        foreign = self.make_character(owner=self.stranger, name="Чужой")
        response = self.client.post(
            "/api/v1/tags/", {"name": "тест", "characters": [foreign.pk]}, format="json"
        )
        self.assertEqual(response.status_code, 400)


class CharacterTagsActionTests(CharactersApiTestCase):
    def test_assign_and_remove_tag(self):
        self.auth()
        character = self.make_character()
        tag = Tag.objects.create(owner=self.owner, name="спб")

        url = f"/api/v1/characters/{character.pk}/tags/"
        response = self.client.post(url, {"add": [tag.pk]}, format="json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["tags"][0]["name"], "спб")

        # фильтрация по тегу (SPEC-006)
        data = self.client.get("/api/v1/characters/?tag=спб").json()
        self.assertEqual(data["count"], 1)

        response = self.client.post(url, {"remove": [tag.pk]}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tags"], [])

    def test_foreign_tag_id_400(self):
        self.auth()
        character = self.make_character()
        foreign_tag = Tag.objects.create(owner=self.stranger, name="чужой")
        response = self.client.post(
            f"/api/v1/characters/{character.pk}/tags/", {"add": [foreign_tag.pk]}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_tagging_foreign_character_404(self):
        self.auth(self.stranger)
        character = self.make_character()  # принадлежит self.owner
        tag = Tag.objects.create(owner=self.stranger, name="мой")
        response = self.client.post(
            f"/api/v1/characters/{character.pk}/tags/", {"add": [tag.pk]}, format="json"
        )
        self.assertEqual(response.status_code, 404)


class GroupApiTests(CharactersApiTestCase):
    def test_group_crud_with_members(self):
        self.auth()
        marius = self.make_character(name="Мариус")
        anna = self.make_character(name="Анна")

        response = self.client.post(
            "/api/v1/groups/", {"name": "Котерия", "members": [marius.pk, anna.pk]}, format="json"
        )
        self.assertEqual(response.status_code, 201, response.content)
        group_id = response.json()["id"]
        self.assertEqual(CharacterGroup.objects.get(pk=group_id).members.count(), 2)

        # фильтрация по группе (SPEC-006)
        data = self.client.get(f"/api/v1/characters/?group={group_id}").json()
        self.assertEqual(data["count"], 2)

        response = self.client.patch(
            f"/api/v1/groups/{group_id}/", {"members": [marius.pk]}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CharacterGroup.objects.get(pk=group_id).members.count(), 1)

    def test_group_cannot_include_foreign_character(self):
        self.auth()
        foreign = self.make_character(owner=self.stranger, name="Чужой")
        response = self.client.post(
            "/api/v1/groups/", {"name": "Котерия", "members": [foreign.pk]}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_group_owner_isolation(self):
        group = CharacterGroup.objects.create(owner=self.owner, name="Котерия")
        self.auth(self.stranger)
        self.assertEqual(self.client.get(f"/api/v1/groups/{group.pk}/").status_code, 404)
