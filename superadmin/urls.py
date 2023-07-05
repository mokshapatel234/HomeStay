from django.urls import path
from .views import *


urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('index', Index.as_view(), name="index"),

    path('addClient', add_client, name='add_client'),
    path('listClients', list_clients, name='list_clients'),
    path('updateClient/<uuid:id>/', update_client, name='update_client'),
    path('deleteClient/<uuid:id>/', delete_client, name='delete_client'),

    path('addCommission', add_commission, name='add_commission'),
    path('listCommission', list_commission, name='list_commission'),
    path('updateCommission/<uuid:id>/', update_commission, name='update_commission'),
    path('deleteCommission/<uuid:id>/', delete_commission, name='delete_commission'),



    path('addState', add_state, name='add_state'),
    path('listState', list_state, name='list_state'),
    path('updateState/<uuid:id>/', update_state, name='update_state'),
    path('deleteState/<uuid:id>/', delete_state, name='delete_state'),

    path('get_cities/', get_cities, name='get-cities'),
    path('get_areas/', get_areas, name='get-areas'),


    path('addCity', add_city, name='add_city'),
    path('listCities', list_cities, name='list_cities'),    
    path('updateCity/<uuid:id>/', update_city, name='update_city'),
    path('deleteCity/<uuid:id>/', delete_city, name='delete_city'),

    path('addArea', add_area, name='add_area'),
    path('listAreas', list_areas, name='list_areas'),
    path('updateArea/<uuid:id>/', update_area, name='update_area'),
    path('deleteArea/<uuid:id>/', delete_area, name='delete_area'),

    path('addProperty', add_property, name='add_property'),
    path('listProperties', list_properties, name='list_properties'),
    path('updateProperty/<uuid:id>/', update_property, name='update_property'),
    path('deleteProperty/<uuid:id>/', delete_property, name='delete_property'),
    
    path('addCustomer', add_customer, name='add_customer'),
    path('listCustomers', list_customers, name='list_customers'),
    path('updateCustomer/<uuid:id>/', update_customer, name='update_customer'),
    path('deleteCustomer/<uuid:id>/', delete_customer, name='delete_customer'),

    path('addTermsPolicy/', add_terms_policy, name="add_terms_policy"),

    # path("password_reset",password_reset_request.as_view(), name="admin_password_reset"),



]
