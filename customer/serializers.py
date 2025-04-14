from rest_framework import serializers

from customer.models import Customer


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
