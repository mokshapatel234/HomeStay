from django.urls import path
from .views import *


urlpatterns = [
    path('register/', RegisterApi.as_view(), name="register_client"),
    path('login/', LoginApi.as_view(), name="login_client"),
    path('forgotPassword/', ForgotPasswordApi.as_view(), name="forgot_password"),
    path('otpVerify/', OtpVerificationApi.as_view(), name="otp_verify"),
    path('resetPassword/', ResetPasswordApi.as_view(), name="reset_password"),
    path('getArea/', AreaListApi.as_view(), name='get_area'),
    path('getCity/', CityListApi.as_view(), name='get_city'),
    path('getState/', StateListApi.as_view(), name='get_state'),
    path('getDashboard/', DashboardPropertyApi.as_view(), name='get_dashboard'),
    path('customerProfile/', CustomerProfileApi.as_view(), name='customer_profile'),
    path('propertyDetail/<uuid:id>/', PropertyDetailApi.as_view(), name='property_detail'),
    path('bookProperty/', BookPropertyApi.as_view(), name='book_property_list'),
    path('bookProperty/<uuid:id>/', BookPropertyApi.as_view(), name='book_property'),
    path('propertyWishlist/', wishlistApi.as_view(), name="property_wishlist"),
    path('propertyWishlist/<uuid:id>/', wishlistApi.as_view(), name="add_property_wishlist"),
    path('termsPolicy/', TermsAndPolicyApi.as_view(), name='terms_and_policy'),


]