from rest_framework import serializers
from .models import PlaidAccount
import logging

class PlaidAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaidAccount
        fields = ['id', 'institution', 'created_at', 'updated_at', 'connection_type', 'connection_data']
        # Excluding sensitive fields like access_token and item_id