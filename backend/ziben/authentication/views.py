from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from adrf.views import APIView
from adrf import generics
from asgiref.sync import sync_to_async

from .serializers import RegisterSerializer
from .models import CustomUser
from ziben.settings import FRONTEND_URL, DEFAULT_FROM_EMAIL


# Create your views here.


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    async def acreate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            await sync_to_async(serializer.is_valid)(raise_exception=True)
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
        print(uidb64)
        print(token)

        id = int(force_str(urlsafe_base64_decode(uidb64)))
        print(id)
        try:
            user = await CustomUser.objects.aget(pk=id, is_active=False)
        except:
            return Response(
                {"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
            )

        user.is_active = True
        await user.asave()

        return Response(
            {"message": "User is registered"}, status=status.HTTP_202_ACCEPTED
        )
