from django.urls import path
from .views import *

urlpatterns = [
    path('register/', Register.as_view()),
    path('email_send/', EmailSend.as_view()),
    path('email_validate/', EmailValidate.as_view()),
    path('restore_password/', RestorePassword.as_view()),
    path('change_password/', ChangePassword.as_view()),
    path('login_in/', LoginIn.as_view()),
    path('add_payment_card/', AddPaymentCard.as_view()),
    path('rsa/', RSAView.as_view()),
    path('profile/', UserProfile.as_view()),
    path('change_avatar/', ChangeImage.as_view()),
    path('logout/', LogOut.as_view()),
]
