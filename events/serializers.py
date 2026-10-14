
from rest_framework import serializers
from .models import Event
from django.contrib.auth import authenticate

from rest_framework import serializers
from .models import Registration
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        data["user"] = user
        return data        





class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ["id", "user", "event", "registered_at"]
        read_only_fields = ["id", "user", "registered_at"]
