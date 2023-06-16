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
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from clientapi.serializers import RegisterSerializer, LoginSerializer, ResetPasswordSerializer
from .utils import generate_token
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt


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


class LoginAPIView(generics.GenericAPIView):
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
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ForgotPassword(generics.GenericAPIView):
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
        

class OtpVerification(generics.GenericAPIView):
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



class ResetPassword(generics.GenericAPIView):
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
