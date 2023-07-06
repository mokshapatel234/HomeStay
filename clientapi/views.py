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
from clientapi.serializers import RegisterSerializer, LoginSerializer,\
      ResetPasswordSerializer, ClientProfileSerializer,PropertiesListSerializer, PropertiesSerializer,\
      BookPropertySerializer, TermsAndPolicySerializer, BookingDetailSerializer, CustomerSerializer
from .utils import generate_token
from django.views.decorators.csrf import csrf_exempt
from .authentication import JWTAuthentication, IsClientVerified
from rest_framework.parsers import MultiPartParser


class TermsAndPolicyApi(generics.GenericAPIView):
    permission_classes =(permissions.AllowAny, )
    
    def get(self, request):
        terms_and_policy = TermsandPolicy.objects.first()  
        serializer = TermsAndPolicySerializer(terms_and_policy) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# Register Client
class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            serializer = self.serializer_class(data = request.data, context={'request': request})
        
            if serializer.is_valid():
                user = serializer.save()
                response = Response({"result":True,
                                    "data":serializer.data,
                                    "message": "Customer created successfully",}, status=status.HTTP_201_CREATED)
                return response
            
            errors = [str(error[0]) for error in serializer.errors.values()]
            response = Response({"result":False,
                                "message":", ".join(errors)}, status=status.HTTP_400_BAD_REQUEST)
            return response
        except:
            response = Response({"result":False,
                                "message": "Invalid data input. Please provide appropriate credentials"}, status=status.HTTP_400_BAD_REQUEST)
            return response
    



# Login client and get JWT token for further authentication
class LoginApi(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny, )
    @csrf_exempt
        
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                client = serializer.validated_data['client']
                
                token = generate_token(str(client.id))
                
                user_data = {
                    "id": client.id,
                    "first_name": client.first_name,
                    "last_name":client.last_name,
                    "email":client.email,
                    "password":client.password,
                    "contact_no":client.contact_no,
                    'token': str(token.decode("utf-8"))
                }
                return Response({"result":True, 
                                    "data":user_data,
                                    "message":"Login successfull!!",         
                                     })
            errors = [str(error[0]) for error in serializer.errors.values()]
            response = Response({"result":False,
                                "message":", ".join(errors)}, status=status.HTTP_400_BAD_REQUEST)
            return response
        except:
            response = Response({"result":False,
                                "message": "Invalid data input. Please provide appropriate credentials"}, status=status.HTTP_400_BAD_REQUEST)
            return response


# Forgot Password

class ForgotPasswordApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            email = request.data['email']
            if email:
                print(email)
            else:
                print("error")
            client_obj = Client.objects.get(email=email)
            generated_otp = random.randint(1111, 9999)
            # otp_verification_link = request.build_absolute_uri(reverse('otpverify'))
            request.session['client'] = str(client_obj.id)
            request.session['otp'] = generated_otp
            subject = 'Acount Recovery'

            template_data = {'otp':generated_otp}
            html_message = render_to_string('verify_otp.html', template_data)

            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [email]

            email = EmailMultiAlternatives(subject, body=None, from_email=from_email, to=to_email)
            email.attach_alternative(html_message, "text/html")
            email.send()
            return Response({'result':True,
                             'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'result':False,
                            'message':'Please provide valid email address'},status=status.HTTP_400_BAD_REQUEST)



# OTP Verification
class OtpVerificationApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            client_otp = request.data['otp']
            try:
                if client_otp == str(request.session.get('otp')):
                    del request.session['otp']

                    return Response({'result':True,
                                    'message':'Otp Verified'},status=status.HTTP_200_OK)
                else:
                    return Response({'result':False,
                                    'message':'Wrong Otp'},status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'result':False,
                                "message": 'Error To Verify Otp'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'result':False,
                            'message':'Please provide valid Otp'},status=status.HTTP_404_NOT_FOUND)
     


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
                    return Response({'result':True,
                                    'message':'Password Changed Successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'result':False,
                                    'message':'Password Not Matched'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'result':False,
                                'message':'Cannot Change Password Without otp verification '},status=status.HTTP_400_BAD_REQUEST)
        except:

            return Response({'result':False,
                            'message':'Cannot Change Password Without otp verification'},status=status.HTTP_404_NOT_FOUND)


# Clinet's property management

class ClientProfileApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
   
    
    def get(self,request):
        try:
            serializer = ClientProfileSerializer(request.user)
    
            return Response({"result":True,
                            "data":serializer.data,
                            "message":"Client found successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message": "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        


    def put(self, request):
        try: 
            serializer = ClientProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"result":True,
                                "data":serializer.data,
                                'message':'Profile Updated'},status=status.HTTP_201_CREATED)
            else:
                return Response({"result":False,
                                "message": "Error in updating profile"}, status=status.HTTP_400_BAD_REQUEST)
       
        except:
            return Response({"result":False,
                            "message": "Error in updating profile"}, status=status.HTTP_400_BAD_REQUEST)
 
# Property Management
class PropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = (MultiPartParser, )


    def get(self, request):
        try:
            properties = request.user.properties.all()
            serializer = PropertiesListSerializer(properties, many=True)
            return Response({'result':True,
                            'data':serializer.data,
                            "message":"property found successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message":"Property not available"}, status=status.HTTP_400_BAD_REQUEST)  

    
    def post(self, request):
        try: 
            images = request.FILES.getlist('images')
            videos = request.FILES.getlist('videos')
            terms = request.POST.get('terms')

            serializer = PropertiesSerializer(data=request.data, context={'request': request})
            print(request.data)
            request.data.pop('images')
            request.data.pop('videos')
            request.data.pop('terms')

            if serializer.is_valid():
                property_instance = serializer.save(owner=request.user)
                
                for image in images:
                    PropertyImage.objects.create(property=property_instance, image=image)

                for video in videos:
                    PropertyVideo.objects.create(property=property_instance, video=video)

                PropertyTerms.objects.create(property=property_instance, terms=terms)

                return Response({"result":True,
                                "data":serializer.data,
                                'message':'Property added successfully'},status=status.HTTP_201_CREATED)
            else:
                return Response({"result":False,
                                "message": "Error in property insertion"}, status=status.HTTP_400_BAD_REQUEST)
       
        except:
            return Response({"result":False,
                            "message": "Error in property insertion"}, status=status.HTTP_400_BAD_REQUEST)
 
    def put(self, request, property_id):
        try:
            property_obj = request.user.properties.get(id=property_id)
            
            serializer = PropertiesSerializer(property_obj, data=request.data)
            request.data.pop('images')
            request.data.pop('videos')
            request.data.pop('terms')

            if serializer.is_valid():
                property_instance = serializer.save()

                property_obj.images.all().delete()
                property_obj.videos.all().delete()
                property_obj.terms.all().delete()

                images = request.FILES.getlist('images')
                for image in images:
                    PropertyImage.objects.create(property=property_obj, image=image)


                videos = request.FILES.getlist('videos')
                for video in videos:
                    PropertyVideo.objects.create(property=property_obj, video=video)

                terms = request.POST.get('terms')
                PropertyTerms.objects.create(property=property_obj, terms=terms)


                return Response({"result":True,
                                "data":serializer.data,
                                'message':'Property Updated'},status=status.HTTP_201_CREATED)
            else:
                return Response({"result":False,
                                "message": "Error in updating property"}, status=status.HTTP_400_BAD_REQUEST)
       
        except Exception as e:
            return Response({"result":False,
                            "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 


    def delete(self, request, property_id):
        try:
            property_instance = request.user.properties.get(id=property_id)
            property_instance.delete()
            return Response({'result':True,
                            "message":"property deleted successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message":"Property not available"}, status=status.HTTP_400_BAD_REQUEST)  
    



class DashboardApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    
    def get(self, request):
        try:
            properties = Properties.objects.order_by('-created_at')[:10]
            bookings = Bookings.objects.order_by('-created_at')[:10]

            property_serializer = PropertiesListSerializer(properties, many=True)
            booking_serializer = BookPropertySerializer(bookings, many=True)

            data = {
                'properties': property_serializer.data,
                'bookings': booking_serializer.data
            }

            return Response({"result":True,
                            "data":data,
                            'message':'found successfully'},status=status.HTTP_201_CREATED)
            
        except:
            return Response({"result":False,
                            "message": "Error in dashbord"}, status=status.HTTP_400_BAD_REQUEST)


class BookPropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            properties = request.user.properties.all()
            user = request.user
            bookings = Bookings.objects.filter(property__owner=user)

            serializer = BookPropertySerializer(bookings, many=True)
            
            return Response({
                'result': True,
                'data': serializer.data,
                'message': 'Booking history'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'result': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, id):
        try:
            booking = Bookings.objects.get(id=id)
            property = booking.property
            customer = booking.customer

            property_serializer = PropertiesListSerializer(property)
            customer_serializer = CustomerSerializer(customer)
            booking_serializer = BookingDetailSerializer(booking)

            serializer_data = {
                'property': property_serializer.data,
                'customer': customer_serializer.data,
                'booking': booking_serializer.data
            }
            return Response({'result':True,
                            'data':serializer_data,
                            "message":"Booking found successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'result': False,
                'message': str(e) },status=status.HTTP_400_BAD_REQUEST)  
    

  




