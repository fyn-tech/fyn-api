from rest_framework.permissions import BasePermission


class IsAuthenticatedRunner(BasePermission):
    """
    Custom permission for runner authentication.
    Allows access if the request has a valid runner token.
    """

    def has_permission(self, request, view):
        # Check if we have a runner token authentication
        return (
            hasattr(request, "user")
            and request.user
            and hasattr(request.user, "is_active")
            and request.user.is_active
        )
