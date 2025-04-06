from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlaidAccountViewSet

router = DefaultRouter()
router.register(r'plaidstuff', PlaidAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
