from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
# from .views import PlaidAccountViewSet

# router = DefaultRouter()
# router.register(r'plaidstuff', PlaidAccountViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('login/', views.login_view, name='api-login'),
    path('logout/', views.logout_view, name='api-logout'),
    path('signup/', views.signup_view, name='api-signup'),
    path('session/', views.session_view, name='api-session'),

]