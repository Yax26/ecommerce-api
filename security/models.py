from django.db import models

from common.models import Audit


class CustomerAuthTokens(Audit):
    class Meta:
        db_table = 'ws_customer_auth_tokens'

    access_token = models.TextField(null=True, db_column="auth_access_token")
    refresh_token = models.TextField(null=True, db_column="auth_refresh_token")
