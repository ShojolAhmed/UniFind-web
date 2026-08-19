from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Read access to everyone; write access only to the object's owner.
    Assumes the model instance exposes an ``owner`` relation.
    """

    message = 'You must be the owner of this item to modify it.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'owner_id', None) == request.user.id
