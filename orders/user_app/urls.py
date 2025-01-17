from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from user_app.views import RegisterUser, LoginUser, UserDetails, ContactView, ConfirmAccount

app_name = 'user_app'

urlpatterns = [
    path('user/register', RegisterUser.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/login', LoginUser.as_view(), name='user-login'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('user/details', UserDetails.as_view(), name='user-details'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    ]
