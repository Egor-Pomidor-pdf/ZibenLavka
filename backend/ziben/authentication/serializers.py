from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from adrf.serializers import ModelSerializer
from django.utils import timezone
from django.db.models import F
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser
from ziben.base_serializer import BaseAsyncSerializer


class UserSerializer(BaseAsyncSerializer):
    current_money = serializers.SerializerMethodField()
    server_time = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "money",
            "money_per_click",
            "money_per_second",
            "current_money",
            "server_time",
        ]

    def current_money(self, instance: CustomUser):
        now = timezone.now()
        elapsed = int((now - instance.time_money_last_earn).total_seconds())
        return int(instance.money) + elapsed * instance.money_per_second


class RegisterSerializer(BaseAsyncSerializer):

    password = serializers.CharField(write_only=True, max_length=128)
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "access", "refresh")

    def get_access(self, user):
        return str(RefreshToken.for_user(user).access_token)

    def get_refresh(self, user):
        return str(RefreshToken.for_user(user))

    def avalidate(self, data):
        email = data["email"]

        if CustomUser.objects.filter(email=email, is_active=True).aexists():
            raise serializers.ValidationError(
                {"email": "This email is already registered to an active account"}
            )

        validate_password(data["password"])

        return data

    async def acreate(self, validated_data):
        email = validated_data["username"]
        try:
            inactive_user = await CustomUser.objects.aget(email=email, is_active=False)
        except:
            user = await CustomUser.objects.acreate(
                username=validated_data["username"],
                email=validated_data["email"],
            )
            user.set_password(validated_data["password"])
            await user.asave()
            return user
        inactive_user.username = validated_data["username"]
        inactive_user.set_password(validated_data["password"])
        await inactive_user.asave()
        return inactive_user
