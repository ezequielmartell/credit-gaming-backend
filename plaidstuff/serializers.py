from rest_framework import serializers
from .models import PlaidAccount

class PlaidAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaidAccount
        fields = '__all__'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)