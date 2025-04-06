from django.contrib import admin
from .models import PlaidAccount


# Register your models here.
@admin.register(PlaidAccount)
class PlaidItemAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "institution", "created_at"] 
    search_fields = ["user__email", "institution"]
    list_filter = ["created_at"]