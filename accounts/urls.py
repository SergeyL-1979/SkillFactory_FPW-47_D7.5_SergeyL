from django.urls import path, include
from .views import UserEdit, upgrade_me
from allauth.account.views import LoginView, SignupForm


urlpatterns = [
    path("login/", LoginView.as_view(), name="account_login"),
    path('signup/', SignupForm, name='signup'),
    path('profile/', UserEdit.as_view(), name='account_profile'),
    path('upgrade/', upgrade_me, name='upgrade_me'),
]
