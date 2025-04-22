from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import PlaidAccountViewSet

router = DefaultRouter()
router.register(r'plaidstuff', PlaidAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create_link_token/', views.create_link_token, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),

]
