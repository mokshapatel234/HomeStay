from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterApi.as_view(), name="registerclient"),
    path('login/', LoginApi.as_view(), name="loginclient"),
    path('forgotpassword/', ForgotPasswordApi.as_view(), name="forgotpassword"),
    path('otpverify/', OtpVerificationApi.as_view(), name="otpverify"),
    path('resetpassword/', ResetPasswordApi.as_view(), name="reset_password"),
    path('clientprofile/', ClientProfileApi.as_view(), name="client_profile"),
    path('clientproperty/', PropertyApi.as_view(), name="client_property"),
    path('clientproperty/<property_id>', PropertyApi.as_view(), name="client_property_update"),
    path('clientporpertyfiles/<id>', PropertyFilesApi.as_view(), name="client_property_files"),
]
