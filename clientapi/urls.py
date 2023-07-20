from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterApi.as_view(), name="registerclient"),
    path('login/', LoginApi.as_view(), name="login_client"),
    path('forgotPassword/', ForgotPasswordApi.as_view(), name="forgot_password"),
    path('otpVerify/', OtpVerificationApi.as_view(), name="otp_verify"),
    path('resetPassword/', ResetPasswordApi.as_view(), name="reset_password"),
    path('clientProfile/', ClientProfileApi.as_view(), name="client_profile"),
    path('clientProperty/', PropertyApi.as_view(), name="client_property"),
    path('clientProperty/<property_id>', PropertyApi.as_view(), name="client_property_update"),
    path('clientPropertyDetail/<id>', PropertyDetailApi.as_view(), name="client_property_detail"),
    path('propertyBooking/', BookPropertyApi.as_view(), name="client_booked_property"),
    path('bookingDetail/<id>', BookingDetailApi.as_view(), name="client_booked_detail"),
    path('termsPolicy/', TermsAndPolicyApi.as_view(), name='terms_and_policy'),
    path('calender/', CalenderApi.as_view(), name='calender'),
    path('dashboard/', DashboardApi.as_view(), name='dashboard'),
    # path('bankDetail/', ClientBankingApi.as_view(), name='client_bank_detail'),
    # path('accounts/<str:account_id>/products', CreateProductApi.as_view(), name='create-product'),
    # path('accounts/<str:account_id>/products/<str:product_id>/', CreateProductApi.as_view(), name='add_bank_detail'),
    path('bankDetail/',BankingAndProductApi.as_view(), name='client_bank_detail')





]
