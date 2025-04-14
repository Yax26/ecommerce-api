
import datetime
import jwt


from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from django.core.exceptions import PermissionDenied
from django.db.models import Q


from Ecommerce_API import settings

from common.constants import SERIALIZER_IS_NOT_VALID, TOKEN_IS_EXPIRED, USER_NOT_FOUND

from customer.models import Customer

from exceptions.generic import CustomBadRequest, GenericException

from security.serializers import CustomerAuthTokenSerializer
from security.models import CustomerAuthTokens


def get_customer_authentication_token(customer):
    customer_refresh_token = jwt.encode(
        payload={
            "token_type": "refresh",
            "customer_id": customer.customer_id,
            "email": customer.email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + settings.REFRESH_TOKEN_LIFETIME
        },
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    customer_access_token = jwt.encode(
        payload={
            "token_type": "access",
            "customer_id": customer.customer_id,
            "email": customer.email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) + settings.ACCESS_TOKEN_LIFETIME
        },
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return {
        "customer_access_token": customer_access_token,
        "customer_refresh_token": customer_refresh_token
    }


def save_token(token):
    customer_auth_token_serializer = CustomerAuthTokenSerializer(
        data={
            "access_token": token["customer_access_token"],
            "refresh_token": token["customer_refresh_token"]
        }
    )

    if customer_auth_token_serializer.is_valid():
        customer_auth_token_serializer.save()
    else:
        raise CustomBadRequest(message=SERIALIZER_IS_NOT_VALID)


class CustomerJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            header = request.headers.get("authorization")

            if "authorization" not in request.headers:
                raise PermissionDenied()

            customer_token = header.split(" ")[1]

            if not CustomerAuthTokens.objects.filter(
                    Q(access_token=customer_token) | Q(
                        refresh_token=customer_token)
            ).exists():
                raise AuthenticationFailed(detail=TOKEN_IS_EXPIRED)

            claims = jwt.decode(customer_token, key=settings.JWT_SECRET, algorithms=[
                                settings.JWT_ALGORITHM])

            customer = Customer.objects.get(
                customer_id=claims["customer_id"],
                email=claims["email"],
                is_deleted=False
            )

            return customer, claims

        except PermissionDenied as e:
            raise PermissionDenied()

        except AuthenticationFailed as e:
            raise AuthenticationFailed(detail=TOKEN_IS_EXPIRED)

        except Customer.DoesNotExist:
            return GenericException(message=USER_NOT_FOUND)

        except Exception:
            return GenericException()
