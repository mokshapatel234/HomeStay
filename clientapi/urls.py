from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterApi.as_view(), name="registerclient"),
    path('login/', LoginAPIView.as_view(), name="loginclient"),
    path('forgotpassword/', ForgotPassword.as_view(), name="forgotpassword"),
    path('otpverify/', OtpVerification.as_view(), name="otpverify"),
    path('resetpassword/', ResetPassword.as_view(), name="reset_password")
]
