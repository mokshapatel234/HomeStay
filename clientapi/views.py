from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import serializers
from django.http import JsonResponse
import random
from django.urls import reverse
from superadmin.models import *
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.mail import send_mail
from clientapi.serializers import RegisterSerializer, LoginSerializer,\
      ResetPasswordSerializer, ClientProfileSerializer, PropertiesSerializer, PropertyImageSerializer
from .utils import generate_token
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
from .authentication import JWTAuthentication
from rest_framework.parsers import JSONParser, MultiPartParser

# Register Client
class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data = request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            response = Response({"client":serializer.data,
                                 "message": "Client created successfully",}, status=status.HTTP_201_CREATED)
            return response
        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response

# Login client and get JWT token for further authentication
class LoginApi(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (AllowAny,)
    @csrf_exempt
        
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                client = serializer.validated_data['client']
                token = generate_token(str(client.id))
                response_data = {'token': str(token.decode("utf-8"))}  
                return JsonResponse({"msg":"Login successfull!!",
                                     "data":response_data
                                     })
            else:
                raise serializers.ValidationError(serializer.errors)
        except Exception as e:
            print(e)
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Forgot Password
class ForgotPasswordApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            email = request.POST['email']
            client_obj = Client.objects.get(email=email)
            generated_otp = random.randint(1111, 9999)
            otp_verification_link = request.build_absolute_uri(reverse('otpverify'))
            request.session['client'] = str(client_obj.id)
            request.session['otp'] = generated_otp
            subject = 'Acount Recovery'
            message = f'''your otp for account recovery is {generated_otp}
                        Please click on the below link to verify your otp
                        {otp_verification_link}'''
            email_from = settings.EMAIL_HOST_USER
            recepient = [client_obj.email, ]
            send_mail(subject, message, email_from, recepient)
            return Response({'detail':'Otp Sent To Email'},status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'detail':str(e)},status=status.HTTP_400_BAD_REQUEST)
        
# OTP Verification
class OtpVerificationApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            client_otp = request.POST['otp']
            try:
                if client_otp == str(request.session.get('otp')):
                    del request.session['otp']
                    reset_password_link = request.build_absolute_uri(reverse('reset_password'))

                    return Response({'detail':'Otp Verified', "link":reset_password_link},status=status.HTTP_200_OK)
                else:
                    return Response({'detail':'Wrong Otp'},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail':'Error To Verify Otp'},status=status.HTTP_404_NOT_FOUND)


# Reset Password
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
                    client_obj = Client.objects.get(id = str(request.session.get('client')))
                    client_obj.password = new_password
                    client_obj.save()
                    del request.session['client']
                    return Response({'detail':'Password Changed Successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'detail':'Password Not Matched'},status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({'detail':'Cannot Change Password Without otp verification '},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           
            return Response({'detail':str(e)},status=status.HTTP_404_NOT_FOUND)

# Clinet's property management

class ClientProfileApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
   
    
    def get(self,request):
        try:
            serializer = ClientProfileSerializer(request.user)
    
            return Response(serializer.data, status=status.HTTP_200_OK)
                   
        except Exception as e:
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        try: 
            serializer = ClientProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail':'Profile Updated'},status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
        except Exception as e:
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Property Management
class PropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    def get(self, request):
        try:
            properties = request.user.properties.all()
            serializer = PropertiesSerializer(properties, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)  
    
    
    def post(self, request):
        try: 
            serializer = PropertiesSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(owner=request.user)  
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, property_id):
        try:
            property_instance = request.user.properties.get(id=property_id)
            serializer = PropertiesSerializer(property_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        except Properties.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, property_id):
        try:
            property_instance = request.user.properties.get(id=property_id)
            property_instance.delete()
            return Response({"detail":"Proeprty deleted successfully!"})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


     
class PropertyFilesApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    parser_classes = (MultiPartParser,)

    def post(self, request, id):
        try:
            property_obj = Properties.objects.get(id=id)

            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_obj, image=image)
            videos = request.FILES.getlist('videos')
            for video in videos:
                PropertyVideo.objects.create(property=property_obj, video=video)
            return Response({"detail":"Images and videos uploaded successfully."}, status=status.HTTP_201_CREATED)

        except Properties.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request, id):
        try:
            property_obj = Properties.objects.get(id=id)

            property_obj.images.all().delete()
            property_obj.videos.all().delete()

            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_obj, image=image)

            videos = request.FILES.getlist('videos')
            for video in videos:
                PropertyVideo.objects.create(property=property_obj, video=video)

            return Response({"detail": "Images and videos updated successfully."}, status=status.HTTP_200_OK)

        except Properties.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)





