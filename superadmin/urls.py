from django.urls import path
from .views import *



urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('index', Index.as_view(), name="index"),

    path('addClient', add_client, name='add_client'),
    path('allClients', all_clients, name='all_clients'),
    path('updateClient/<uuid:id>/', update_client, name='update_client'),
    path('deleteClient/<uuid:id>/', delete_client, name='delete_client'),

    path('addProperty', add_property, name='add_property'),
    path('allProperties', all_properties, name='all_properties'),
    path('updateProperty/<uuid:id>/', update_property, name='update_property'),
    path('deleteProperty/<uuid:id>/', delete_property, name='delete_property'),
    
    path('addCustomer', add_customer, name='add_customer'),
    path('allCustomers', all_customers, name='all_customers'),
    path('updateCustomer/<uuid:id>/', update_customer, name='update_customer'),
    path('deleteCustomer/<uuid:id>/', delete_customer, name='delete_customer'),

    path('addTermsPolicy/', add_terms_policy, name="add_terms_policy"),
    ]
