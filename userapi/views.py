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
from userapi.serializers import RegisterSerializer, LoginSerializer, ResetPasswordSerializer, AreaSerializer, CitySerializer, \
    StateSerializer, PropertiesSerializer
from .utils import generate_token
from django.views.decorators.csrf import csrf_exempt
from .authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser
import json


# Create your views here.




class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data = request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            token = generate_token(str(user.id))
            response_data = {'token': str(token.decode("utf-8"))}  
            response = Response({"data":serializer.data,
                                 "user_token":response_data,
                                 "message": "Customer created successfully",}, status=status.HTTP_201_CREATED)
            return response
        response = Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return response

class LoginApi(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny, )
    @csrf_exempt
        
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                customer = serializer.validated_data['customer']
                user_data = {
                    "id": customer.id,
                    "first_name": customer.first_name,
                    "last_name":customer.last_name,
                    "email":customer.email,
                    "password":customer.password,
                    "area":customer.area.name,
                    "contact_no":customer.contact_no,
                }
                token = generate_token(str(customer.id))
                response_data = {'token': str(token.decode("utf-8"))}  
                return JsonResponse({"data":user_data,
                                    "user_token":response_data,
                                    "message":"Login successfull!!",         
                                     })
            else:
                raise serializers.ValidationError(serializer.errors)
        except Exception as e:
            print(e)
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        return Response({'message': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ForgotPasswordApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            email = request.POST['email']
            if email:
                print(email)
            else:
                print("error")
            customer_obj = Customer.objects.get(email=email)
            generated_otp = random.randint(1111, 9999)
            # otp_verification_link = request.build_absolute_uri(reverse('otpverify'))
            request.session['customer'] = str(customer_obj.id)
            request.session['otp'] = generated_otp
            subject = 'Acount Recovery'

            template_data = {'otp':generated_otp}
            html_message = render_to_string('otp_verify.html', template_data)

            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [email]

            email = EmailMultiAlternatives(subject, body=None, from_email=from_email, to=to_email)
            email.attach_alternative(html_message, "text/html")
            email.send()
            return Response({'message': 'Email sent successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)


class OtpVerificationApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            customer_otp = request.POST['otp']
            try:
                if customer_otp == str(request.session.get('otp')):
                    del request.session['otp']
                    reset_password_link = request.build_absolute_uri(reverse('reset_password'))

                    return Response({'message':'Otp Verified', "link":reset_password_link},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Wrong Otp'},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':'Error To Verify Otp'},status=status.HTTP_404_NOT_FOUND)
     

class ResetPasswordApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        try:
            if not request.session.get('otp'):
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)

                new_password = serializer.validated_data['new_password']
                confirm_password = serializer.validated_data['confirm_password']
                if new_password == confirm_password:
                    customer_obj = Customer.objects.get(id = str(request.session.get('customer')))
                    customer_obj.password = new_password
                    customer_obj.save()
                    del request.session['customer']
                    return Response({'message':'Password Changed Successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Password Not Matched'},status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({'message':'Cannot Change Password Without otp verification '},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           
            return Response({'message':str(e)},status=status.HTTP_404_NOT_FOUND)


class AreaListAPIView(generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def get(self, request):
        try:
            city = request.query_params.get('city', None)
            
            if city:
                areas = Area.objects.filter(city=city)
                print(areas)
            else:
                areas = Area.objects.all()
            
            serializer = AreaSerializer(areas, many=True)
            return Response({"data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


class CityListAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        try:
            state = request.query_params.get('state', None)
            
            if state:
                city = City.objects.filter(state=state)
            else:
                city = City.objects.all()
            
            serializer = CitySerializer(city, many=True)
            return Response({"data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


class StateListAPIView(generics.GenericAPIView):

    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)
    def get(self, request):
        try:
            state = State.objects.all()
            print(state)
            serializer = StateSerializer(state, many=True)
            return Response({"data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":str(e)}, status=status.HTTP_404_NOT_FOUND)
        

class DashboardPropertyView(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        try:
            state = request.query_params.get('state', None)
            city = request.query_params.get('city', None)
            area = request.query_params.get('area', None)

    
            
            if area:
                properties = Properties.objects.filter(area_id__id=area)
            
            elif city:
                properties = Properties.objects.filter(area_id__city__id=city)

            elif state:
                properties = Properties.objects.filter(area_id__city__state__id=state)
            else:
                properties = Properties.objects.all()
            
            serializer = PropertiesSerializer(properties, many=True)
            return Response({"data":serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)


