from django.urls import path
from .views import *


urlpatterns = [
    path('getArea/', AreaListApi.as_view(), name='get_area'),
    path('getCity/', CityListApi.as_view(), name='get_city'),
    path('getState/', StateListApi.as_view(), name='get_state'),

]