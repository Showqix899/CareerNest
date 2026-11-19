from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserRegisterSerializer
from .tasks import send_verification_email


class UserRegisterView(APIView):
    """Register a new user and send them a verification email."""

    # Anyone (not logged in) can register
    permission_classes = [AllowAny]

    def post(self, request):

        # Step 1: validate the data with our serializer
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():

            # Step 2: create the user (is_active=False by default)
            user = serializer.save()

            # Step 3: send the verification email in the background.
            #
            # .delay() puts the task into the Redis queue and returns
            # immediately, so the user doesn't wait for the email to send.
            #
            # transaction.on_commit() waits until the user is really saved
            # in the database before queuing the task. Without it, the
            # worker could run too early and not find the user.
            #
            # str(user.pk) because Celery sends simple data, not UUID objects.
            transaction.on_commit(
                lambda: send_verification_email.delay(str(user.pk))
            )

            return Response(
                {
                    "message": "Registration successful. "
                               "Please check your email to activate your account.",
                    "user": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    """
    Activate a user account from the link inside the verification email.
    The link looks like: /activate/<uidb64>/<token>/
    """

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):

        # Step 1: decode the user id from the link.
        # If the link was changed or broken, decoding fails and user stays None.
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # Step 2: no user found -> the link is invalid
        if user is None:
            return Response(
                {"error": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 3: already activated -> nothing more to do
        if user.is_active:
            return Response(
                {"message": "Your account is already activated."},
                status=status.HTTP_200_OK,
            )

        # Step 4: check the token is correct and not expired
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Activation link is invalid or has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 5: everything is correct -> activate the account.
        # update_fields saves only is_active, nothing else.
        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {"message": "Your account has been activated. You can now log in."},
            status=status.HTTP_200_OK,
        )