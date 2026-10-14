
from rest_framework.permissions import BasePermission


class IsOrganizerOrReadOnly(BasePermission):
    """
    Anyone can view events.
    Only users in the Organizers group can
    create, update, or delete events.
    """

    def has_permission(self, request, view):
        # Allow everyone to read events
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Write operations require an authenticated
        # user belonging to the Organizers group
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name="Organizers"
            ).exists()
        )
