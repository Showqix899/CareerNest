from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers, status
from django.contrib.auth.models import update_last_login



from .utils import get_tokens_for_user
from .models import User
from .serializers import (
                        UserRegisterSerializer,LoginResponseSerializer,
                          LoginSerializer,LoginUserSerializer,LogoutSerializer
                          )
from .tasks import send_verification_email


from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse
)


class UserRegisterView(APIView):
    """Register a new user and send them a verification email."""

    # Anyone (not logged in) can register
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Authentication"],  # groups endpoints together in Swagger
        summary="Register a new user",
        description=(
            "Creates a new user account and sends a verification email. "
            "The account stays inactive until the user clicks the link in the email."
        ),
        # The data the client must send (Swagger builds the form from this)
        request=UserRegisterSerializer,
        # Possible responses, one entry per status code
        responses={
            # inline_serializer describes our custom JSON without a new class
            201: inline_serializer(
                name="RegisterSuccessResponse",
                fields={
                    "message": serializers.CharField(),
                    "user": UserRegisterSerializer(),
                },
            ),
            400: OpenApiExample(  # shown as a simple error example
                "Validation error",
                value={"password": ["Password must contain at least one number."]},
                response_only=True,
                status_codes=["400"],
            ),
        },
        # Example request body shown in Swagger "Try it out"
        examples=[
            OpenApiExample(
                "Valid registration",
                value={
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "phone": "01712345678",
                    "password": "Abcd@1234",
                },
                request_only=True,  # only show it as a request example
            )
        ],
    )

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
    
    @extend_schema(
        tags=["Authentication"],
        summary="Activate account",
        description="Activates the account using the link sent by email.",
        # Describe the two values in the URL
        parameters=[
            OpenApiParameter(
                name="uidb64",
                type=str,
                location=OpenApiParameter.PATH,
                description="Encoded user id from the email link",
            ),
            OpenApiParameter(
                name="token",
                type=str,
                location=OpenApiParameter.PATH,
                description="Activation token from the email link",
            ),
        ],
        responses={
            200: inline_serializer(
                name="ActivateSuccessResponse",
                fields={"message": serializers.CharField()},
            ),
            400: inline_serializer(
                name="ActivateErrorResponse",
                fields={"error": serializers.CharField()},
            ),
        },
    )

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
        
        

#user login view

class LoginView(APIView):
    
    """login business logic"""
    
    permission_classes=[AllowAny]
    
# @extend_schema only changes what Swagger shows. It does not change how the code runs.
    @extend_schema(
        tags=["Authentication"],
        summary="Login",
        description=(
            "Send your email and password. If they are correct and the account "
            "is activated, you get a short-lived access token and a long-lived refresh token."
        ),
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
        examples=[
            OpenApiExample(
                "Login example",
                value={"email": "test@example.com", "password": "Abcd@1234"},
                request_only=True,
            )
        ],
    )
    
    def post(self,request):
        
        """pass the email and password in the Login serializer"""
        serializer = LoginSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True) #check if the provided credentials are correct or not via serializer
        
        user = serializer.validated_data["user"] #get the user from validated data (In serialzer we set attrs[user])
        
        tokens = get_tokens_for_user(user) #generate jwt tokens 
        
        update_last_login(None,user)
        
        return Response(
            {
                "access":tokens["access"],
                "refresh":tokens["refresh"],
                "user":LoginUserSerializer(user).data
            },
            status=status.HTTP_200_OK
        )
        
        
        
class LogoutView(APIView):
    """Log the user out by blacklisting their refresh token."""

    # Only a logged-in user can log out, so the request must have a valid
    # access token: "Authorization: Bearer <access token>"
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Logout",
        description="Blacklists the refresh token so it can't be used again.",
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description="Logged out successfully."),
            400: OpenApiResponse(description="Invalid or expired refresh token."),
        },
    )
    def post(self, request):

        # Step 1: give the refresh token to the serializer.
        # context={"request": request} lets the serializer know who the
        # logged-in user is (used for the "belongs to you" check).
        serializer = LogoutSerializer(
            data=request.data,
            context={"request": request},
        )

        # Step 2: validate. A bad token automatically returns a 400 error.
        serializer.is_valid(raise_exception=True)

        # Step 3: blacklist the refresh token
        serializer.save()

        # Step 4: tell the client it worked
        return Response(
            {"message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )