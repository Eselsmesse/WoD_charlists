from django.urls import path

from . import views

urlpatterns = [
    path("lines/", views.LineListView.as_view(), name="line-list"),
    path("lines/<slug:code>/", views.LineDetailView.as_view(), name="line-detail"),
    path("lines/<slug:code>/traits/", views.TraitListView.as_view(), name="line-traits"),
    path("lines/<slug:code>/clans/", views.ClanListView.as_view(), name="line-clans"),
    path("lines/<slug:code>/archetypes/", views.ArchetypeListView.as_view(), name="line-archetypes"),
    path(
        "lines/<slug:code>/creation-rules/",
        views.CreationRulesView.as_view(),
        name="line-creation-rules",
    ),
]
