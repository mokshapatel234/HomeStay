from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterApi.as_view(), name="registerclient"),
    path('login/', LoginApi.as_view(), name="login_client"),
    path('verifyemail/', EmailVerificationApi.as_view(), name="verify_email"),
    path('emailotpverify/', EmailOTPVerifyApi.as_view(), name="email_otp_verify"),
    path('forgotpassword/', ForgotPasswordApi.as_view(), name="forgot_password"),
    path('otpverify/', OtpVerificationApi.as_view(), name="otp_verify"),
    path('resetpassword/', ResetPasswordApi.as_view(), name="reset_password"),
    path('clientprofile/', ClientProfileApi.as_view(), name="client_profile"),
    path('clientproperty/', PropertyApi.as_view(), name="client_property"),
    path('clientproperty/<property_id>', PropertyApi.as_view(), name="client_property_update"),
]
