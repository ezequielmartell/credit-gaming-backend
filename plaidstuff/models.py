from django.db import models
from users.models import CustomUser
from django.core.exceptions import ValidationError
# Create your models here.



class PlaidAccount(models.Model):
    """
    Model to store Plaid Item information.
    """
    institution = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, blank=True)
    item_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    CONNECTION_CHOICES = [
        ('manual', 'Manual'),
        ('plaid', 'Plaid'),
    ]
    connection_type = models.CharField(max_length=10, choices=CONNECTION_CHOICES, default='manual')
    connection_data = models.JSONField(default=list)

    def __str__(self):
        return self.institution
    
    def clean(self):
        super().clean()
        if not isinstance(self.connection_data, list):
            raise ValidationError("Data must be a list.")