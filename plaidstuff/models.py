from django.db import models
from users.models import CustomUser
# Create your models here.



class PlaidAccount(models.Model):
    """
    Model to store Plaid Item information.
    """
    access_token = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.institution