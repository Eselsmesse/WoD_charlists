from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Объект доступен только владельцу.

    Кверисеты вьюх и так фильтруются по owner (чужой id даёт 404, не раскрывая
    существование объекта); это страховка на уровне объекта.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id
