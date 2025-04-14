from django.db import models

from common.models import Audit


class Customer(Audit):
    class Meta:
        db_table = 'ws_customer'

    customer_id = models.BigAutoField(primary_key=True)

    first_name = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)

    email = models.EmailField(unique=True)
