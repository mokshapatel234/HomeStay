from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
import uuid


urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('index', Index.as_view(), name="index"),

    path('add_client', add_client, name='add_client'),
    path('all_clients', all_clients, name='all_clients'),
    path('update_client/<uuid:id>/', update_client, name='update_client'),
    path('delete_client/<uuid:id>/', delete_client, name='delete_client'),

    path('add_property', add_property, name='add_property'),
    path('all_properties', all_properties, name='all_properties'),
    path('update_property/<uuid:id>/', update_property, name='update_property'),
    path('delete_property/<uuid:id>/', delete_property, name='delete_property'),
    
    path('add_customer', add_customer, name='add_customer'),
    path('all_customers', all_customers, name='all_customers'),
    path('update_customer/<uuid:id>/', update_customer, name='update_customer'),
    path('delete_customer/<uuid:id>/', delete_customer, name='delete_customer'),


]
