from django.urls import path

from . import views

urlpatterns = [
    path(
        "characters/<int:character_id>/share/",
        views.ShareLinkCreateView.as_view(),
        name="share-create",
    ),
    path(
        "characters/<int:character_id>/share/<uuid:token>/",
        views.ShareLinkRevokeView.as_view(),
        name="share-revoke",
    ),
    path("shared/<uuid:token>/", views.SharedCharacterView.as_view(), name="shared-detail"),
    path(
        "shared/<uuid:token>/copy/",
        views.SharedCharacterCopyView.as_view(),
        name="shared-copy",
    ),
]
