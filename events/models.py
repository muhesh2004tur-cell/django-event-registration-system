from django.db import models
from django.conf import settings
from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title





class Registration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    event = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
        related_name="registrations"
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_registration"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
