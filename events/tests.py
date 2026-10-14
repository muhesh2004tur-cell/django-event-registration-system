
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Event, Registration

User = get_user_model()


class EventAPITests(APITestCase):

    def setUp(self):
        # Create the Organizers group
        self.organizers_group, _ = Group.objects.get_or_create(
            name="Organizers"
        )

        # Create an organizer user
        self.organizer = User.objects.create_user(
            username="organizer_test",
            password="testpass123"
        )
        self.organizer.groups.add(self.organizers_group)

        # Create a normal user
        self.user = User.objects.create_user(
            username="normal_test",
            password="testpass123"
        )

        # Create a sample event
        self.event = Event.objects.create(
            title="Python Workshop",
            description="Learn Django REST Framework",
            date=timezone.now() + timedelta(days=7),
            location="Coimbatore",
            capacity=2,
        )

    def test_anyone_can_view_events(self):
        response = self.client.get("/api/events/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_organizer_can_create_event(self):
        self.client.force_authenticate(user=self.organizer)

        response = self.client.post(
            "/api/events/",
            {
                "title": "Django Workshop",
                "description": "Learn Django",
                "date": (
                    timezone.now() + timedelta(days=10)
                ).isoformat(),
                "location": "Chennai",
                "capacity": 30,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_normal_user_cannot_create_event(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/events/",
            {
                "title": "Unauthorized Event",
                "description": "Should not be created",
                "date": (
                    timezone.now() + timedelta(days=10)
                ).isoformat(),
                "location": "Chennai",
                "capacity": 30,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_user_can_register_for_event(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Registration.objects.filter(
                user=self.user,
                event=self.event
            ).exists()
        )

    def test_user_cannot_register_twice(self):
        Registration.objects.create(
            user=self.user,
            event=self.event
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_registration_fails_when_event_is_full(self):
        self.event.capacity = 1
        self.event.save()

        # First user takes the only available spot
        Registration.objects.create(
            user=self.user,
            event=self.event,
        )

        # A second user tries to register
        self.client.force_authenticate(user=self.organizer)

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["error"],
            "Sorry, this event is full.",
        )
    
    def test_user_cannot_cancel_another_users_registration(self):
        # Create a registration belonging to the organizer
        registration = Registration.objects.create(
            user=self.organizer,
            event=self.event,
        )

        # Authenticate as a different user
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/api/registrations/{registration.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        # Confirm the original registration still exists
        self.assertTrue(
            Registration.objects.filter(
                id=registration.id
            ).exists()
        )
    
    def test_user_sees_only_their_own_registrations(self):
        # Create registrations for two different users
        Registration.objects.create(
            user=self.user,
            event=self.event,
        )

        another_event = Event.objects.create(
            title="Django Advanced Workshop",
            description="Advanced Django topics",
            date=timezone.now() + timedelta(days=14),
            location="Chennai",
            capacity=20,
        )

        Registration.objects.create(
            user=self.organizer,
            event=another_event,
        )

        # Authenticate as the normal user
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "/api/registrations/my/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["user"],
            self.user.id,
        )
