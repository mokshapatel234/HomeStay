from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterApi.as_view(), name="register_client"),
    path('login/', LoginApi.as_view(), name="login_client"),
    path('forgotPassword/', ForgotPasswordApi.as_view(), name="forgot_password"),
    path('otpVerify/', OtpVerificationApi.as_view(), name="otp_verify"),
    path('resetPassword/', ResetPasswordApi.as_view(), name="reset_password"),
    path('getArea/', AreaListAPIView.as_view(), name='get_area'),
    path('getCity/', CityListAPIView.as_view(), name='get_city'),
    path('getState/', StateListAPIView.as_view(), name='get_state'),
    path('getDashboard/', DashboardPropertyView.as_view(), name='get_dashboard'),
    

]