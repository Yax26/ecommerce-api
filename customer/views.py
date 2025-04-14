import re
import traceback

from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from email_validator import validate_email, EmailNotValidError

from common.constants import (
    AUTHORIZATION_HEADER_MISSING,
    BAD_REQUEST,
    DATA_IS_INVALID,
    INCORRECT_PASSWORD,
    NEW_PASSWORDS_DOES_NOT_MATCH,
    PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20,
    PASSWORD_MUST_HAVE_ONE_NUMBER,
    PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER,
    PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER,
    PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER,
    PASSWORD_UPDATED_SUCCESSFULLY,
    USER_ALREADY_EXISTS,
    USER_LOGGED_IN_SUCCESSFULLY,
    USER_LOGGED_OUT_SUCCESSFULLY,
    USER_NOT_FOUND,
    USER_REGISTERED_SUCCESSFULLY,
    YOUR_CURRENT_PASSWORD_IS_INCORRECT,
)
from common.views import send_registration_email

from customer.models import Customer
from customer.serializers import RegistrationSerializer

from exceptions.generic_response import GenericSuccessResponse
from exceptions.generic import CustomBadRequest, CustomNotFound, GenericException

from security.customer_authorization import CustomerJWTAuthentication, get_customer_authentication_token, save_token
from security.models import CustomerAuthTokens


# Create your views here


class Registration(APIView):
    @staticmethod
    def post(request):
        try:

            if (
                "email" not in request.data or request.data["email"] == "" or
                "password" not in request.data or request.data["password"] == "" or
                "first_name" not in request.data or request.data["first_name"] == "" or
                "last_name" not in request.data or request.data["last_name"] == "" or
                "middle_name" not in request.data or request.data["middle_name"] == "" or
                "address" not in request.data or request.data["address"] == ""
            ):
                return CustomBadRequest(message=BAD_REQUEST)

            validation = validate_email(request.data['email'])

            password = request.data["password"]
            special_characters = r"[\$#@!\*]"

            if len(password) < 8 or len(password) > 20:
                return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
            if re.search('[0-9]', password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_NUMBER)
            if re.search('[a-z]', password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER)
            if re.search('[A-Z]', password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER)
            if re.search(special_characters, password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER)

            if Customer.objects.filter(email=request.data['email']):
                return CustomBadRequest(message=USER_ALREADY_EXISTS)

            registration_serializer = RegistrationSerializer(data=request.data)

            # Hash the password before saving
            request.data["password"] = make_password(request.data["password"])

            if registration_serializer.is_valid(raise_exception=True):

                customer = registration_serializer.save()
                tokens = get_customer_authentication_token(customer)
                save_token(tokens)

                # Uncomment the line below to send a registration email
                # message = f"Hi {customer.first_name},\n\nThank you for registering on our platform. We're excited to have you!\n\nBest Regards,\E-commerce Team"
                # send_registration_email(customer.email, customer.first_name, message=message)

                return GenericSuccessResponse(tokens, message=USER_REGISTERED_SUCCESSFULLY, status=201)

            return CustomBadRequest(message=DATA_IS_INVALID)

        except EmailNotValidError as e:
            return CustomBadRequest(message=str(e))


        except Exception:
            return GenericException()


class Logout(APIView):
    authentication_classes = [CustomerJWTAuthentication]

    @staticmethod
    def delete(request):

        try:
            header = request.headers.get("authorization")

            if not header:
                return CustomBadRequest(message=AUTHORIZATION_HEADER_MISSING)

            token = header.split(" ")[1]

            CustomerAuthTokens.objects.filter(
                Q(access_token=token) | Q(refresh_token=token)).delete()

            return GenericSuccessResponse(message=USER_LOGGED_OUT_SUCCESSFULLY, status=200)

        except Exception:
            return GenericException()


class Login(APIView):
    @staticmethod
    def post(request):
        try:

            if "email" not in request.data or request.data["email"] == "" or "password" not in request.data or request.data["password"] == "":
                return CustomBadRequest(BAD_REQUEST)

            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                return CustomBadRequest(message=BAD_REQUEST)

            validation = validate_email(request.data['email'])

            customer = Customer.objects.get(email=email, is_deleted=False)

            if not check_password(password, customer.password):
                return CustomBadRequest(message=INCORRECT_PASSWORD)

            authentication_tokens = get_customer_authentication_token(customer)
            save_token(authentication_tokens)
            return GenericSuccessResponse(authentication_tokens, message=USER_LOGGED_IN_SUCCESSFULLY, status=201)

        except EmailNotValidError as e:
            return CustomBadRequest(message=str(e))

        except Customer.DoesNotExist:
            return CustomNotFound(message=USER_NOT_FOUND)

        except Exception:
            return GenericException()


class ResetPassword(APIView):
    authentication_classes = [CustomerJWTAuthentication]

    @staticmethod
    def patch(request):
        try:
            if (
                "current_password" not in request.data or request.data["current_password"] == "" or
                "new_password" not in request.data or request.data["new_password"] == "" or
                "confirm_password" not in request.data or request.data["confirm_password"] == ""
            ):
                return CustomBadRequest(message=BAD_REQUEST)

            customer = request.user
            current_password = request.data.get("current_password")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            # if current_password != customer.password:
            #     return CustomBadRequest(message=YOUR_CURRENT_PASSWORD_IS_INCORRECT)

            if not check_password(current_password, customer.password):
                return CustomBadRequest(message=YOUR_CURRENT_PASSWORD_IS_INCORRECT)

            if new_password != confirm_password:
                return CustomBadRequest(message=NEW_PASSWORDS_DOES_NOT_MATCH)

            if len(new_password) < 8 or len(new_password) > 20:
                return CustomBadRequest(message=PASSWORD_LENGTH_SHOULD_BE_BETWEEN_8_TO_20)
            if re.search('[0-9]', new_password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_NUMBER)
            if re.search('[a-z]', new_password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SMALLERCASE_LETTER)
            if re.search('[A-Z]', new_password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_UPPERCASE_LETTER)
            if re.search(r"[\$#@!\*]", new_password) is None:
                return CustomBadRequest(message=PASSWORD_MUST_HAVE_ONE_SPECIAL_CHARACTER)

            customer.password = make_password(new_password)
            customer.save()

            return GenericSuccessResponse(message=PASSWORD_UPDATED_SUCCESSFULLY, status=200)

        except Exception as e:
            return GenericException()
