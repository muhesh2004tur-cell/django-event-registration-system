
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Event,Registration
from .serializers import EventSerializer
from .user_serializers import UserRegistrationSerializer
from .serializers import LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsOrganizerOrReadOnly
from .serializers import RegistrationSerializer
from django.db import transaction
from django.db.models import Count
from .permissions import IsOrganizerOrReadOnly
@api_view(["GET", "POST"])
@permission_classes([IsOrganizerOrReadOnly])
def event_list(request):
    if request.method == "GET":
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsOrganizerOrReadOnly])
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "GET":
        serializer = EventSerializer(event)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = EventSerializer(
            event,
            data=request.data
        )

    elif request.method == "PATCH":
        serializer = EventSerializer(
            event,
            data=request.data,
            partial=True
        )

    elif request.method == "DELETE":
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
@api_view(["POST"])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )

@api_view(["POST"])
def user_login(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_for_event(request):
    event_id = request.data.get("event")

    if not event_id:
        return Response(
            {"error": "Event ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        event = get_object_or_404(
            Event.objects.select_for_update(),
            id=event_id
        )

        if Registration.objects.filter(
            user=request.user,
            event=event
        ).exists():
            return Response(
                {"error": "You are already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration_count = Registration.objects.filter(
            event=event
        ).count()

        if registration_count >= event.capacity:
            return Response(
                {"error": "Sorry, this event is full."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration = Registration.objects.create(
            user=request.user,
            event=event
        )

    serializer = RegistrationSerializer(registration)
    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_registrations(request):
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related("event")

    serializer = RegistrationSerializer(
        registrations,
        many=True
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_registration(request, registration_id):
    registration = get_object_or_404(
        Registration,
        id=registration_id,
        user=request.user
    )

    registration.delete()

    return Response(
        {"message": "Registration cancelled successfully."},
        status=status.HTTP_200_OK
    )
