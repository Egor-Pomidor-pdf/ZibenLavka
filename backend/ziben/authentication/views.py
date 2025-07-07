from django.shortcuts import render
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.permissions import AllowAny
from adrf.views import APIView
from adrf import generics
from asgiref.sync import sync_to_async
import logging

from .serializers import RegisterSerializer
from .models import CustomUser
from ziben.settings import FRONTEND_URL, DEFAULT_FROM_EMAIL

logger = logging.getLogger("auth")


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    async def acreate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            await serializer.ais_valid(raise_exception=True)
            user: CustomUser = await serializer.asave()
        except ValidationError as e:
            if (
                "email" not in request.data
                or "username" not in request.data
                or "password" not in request.data
            ):
                raise e
            try:
                if user := await CustomUser.objects.aget(
                    email=request.data["email"], is_active=False
                ):
                    user.username = request.data["username"]
                    user.set_password(request.data["password"])
                    serializer = self.get_serializer(user)
            except:
                raise e

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        user.email_verification_token = token
        await user.asave()

        # dummy as for now
        url = f"https://{FRONTEND_URL}/accounts/register/{uidb64}/{token}/"

        await sync_to_async(send_mail)(
            "Подтверждение аккаунта Ziben-лавка",
            f"Для подтверждения аккаунта перейдите по ссылке:\n{url}",
            DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(APIView):

    async def post(self, request):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")

        default_token_generator

        id = int(force_str(urlsafe_base64_decode(uidb64)))

        try:
            user = await CustomUser.objects.aget(pk=id, is_active=False)
        except:
            return Response(
                {"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if (
            not user.email_verification_token
            or user.email_verification_token != token
            or not default_token_generator.check_token(user, token)
        ):
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.is_active = True
        user.email_verification_token = None
        await user.asave()

        return Response(
            {"message": "User is registered"}, status=status.HTTP_202_ACCEPTED
        )


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)

    async def post(self, request, *args, **kwargs):

        email = request.data.get("email")
        try:
            user = await CustomUser.objects.aget(email=email)
        except Exception as e:
            return Response(
                {"error": "user not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not user.is_active:
            return Response(
                {"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST
            )

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        user.password_reset_token = token
        await user.asave()

        # dummy as for now
        url = f"https://{FRONTEND_URL}/accounts/password_reset/{uidb64}/{token}/"

        await sync_to_async(send_mail)(
            "Смена пароля аккаунта Ziben-лавки",
            f"Для смены пароля аккаунта перейдите по ссылке:\n{url}",
            DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response({"message": "email is sent"}, status=status.HTTP_200_OK)


class ResetPasswordVerifyAPIView(APIView):
    permission_classes = (AllowAny,)

    async def post(self, request):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        password = request.data.get("password")
        try:
            validate_password(password)
        except DjangoValidationError as ve:
            return Response(ve.error_list, status=status.HTTP_400_BAD_REQUEST)

        id = int(force_str(urlsafe_base64_decode(uidb64)))
        try:
            user = await CustomUser.objects.aget(pk=id, is_active=True)
        except Exception as e:
            logger.info(e)
            return Response(
                {"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if (
            not user.password_reset_token
            or user.password_reset_token != token
            or not default_token_generator.check_token(user, token)
        ):
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.password_reset_token = None
        user.set_password(password)
        await user.asave()

        return Response(
            {"message": "Password of user is changed successfuly"},
            status=status.HTTP_202_ACCEPTED,
        )
