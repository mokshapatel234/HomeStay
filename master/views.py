from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status, generics
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import serializers
from django.http import JsonResponse
import random
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from superadmin.models import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from master.serializers import StateSerializer, CitySerializer, AreaSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser

# Create your views here.



class AreaListApi(generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def get(self, request):
        try:
            city = request.query_params.get('city', None)
            
            if city:
                areas = Area.objects.filter(city=city)
                if not areas:
                    return Response({"result": False,
                                     "message": "No areas found for the provided city ID."},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                areas = Area.objects.all()
            
            serializer = AreaSerializer(areas, many=True)
            area_data = []
            for area in serializer.data:
                area_data.append({
                    "id": area["id"],
                    "name": area["name"]
                })
            return Response({"result":True,
                            "data":area_data, 
                            'message':'Data found successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message": "Error in getting data"}, status=status.HTTP_404_NOT_FOUND)


class CityListApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        try:
            state = request.query_params.get('state', None)
            
            if state:
                city = City.objects.filter(state=state)
                if not city:
                    return Response({"result": False,
                                     "message": "No cities found for the provided state ID."},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                city = City.objects.all()
            
            serializer = CitySerializer(city, many=True)
            city_data = []
            for city in serializer.data:
                city_data.append({
                    "id": city["id"],
                    "name": city["name"]
                })
            return Response({"result":True,
                            "data":city_data,
                            "message":"Data found successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message": "Error in getting data"}, status=status.HTTP_404_NOT_FOUND)


class StateListApi(generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def get(self, request):
        try:
            state = State.objects.all()
            
            serializer = StateSerializer(state, many=True)
            return Response({"result":True,
                            "data":serializer.data,
                            "message":"Data found successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message": "Error in getting data"}, status=status.HTTP_404_NOT_FOUND)
 