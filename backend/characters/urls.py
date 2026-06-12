from rest_framework.routers import DefaultRouter

from .views import CharacterGroupViewSet, CharacterViewSet, TagViewSet

router = DefaultRouter()
router.register("characters", CharacterViewSet, basename="character")
router.register("tags", TagViewSet, basename="tag")
router.register("groups", CharacterGroupViewSet, basename="group")

urlpatterns = router.urls
