from rest_framework import serializers
from .models import PlaidAccount

class PlaidAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaidAccount
        fields = '__all__'
