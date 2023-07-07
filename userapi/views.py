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
from userapi.serializers import RegisterSerializer, LoginSerializer, ResetPasswordSerializer,\
      AreaSerializer, CitySerializer, StateSerializer, DashboardPropertiesSerializer,\
          CustomerProfileSerializer, PropertiesDetailSerializer, BookPropertySerializer,\
              TermsAndPolicySerializer, WishlistSerializer
from .utils import generate_token
from django.views.decorators.csrf import csrf_exempt
from .authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser
from datetime import datetime


# Create your views here.


class TermsAndPolicyApi(generics.GenericAPIView):
    permission_classes =(permissions.AllowAny, )
    
    def get(self, request):
        terms_and_policy = TermsandPolicy.objects.first()  
        serializer = TermsAndPolicySerializer(terms_and_policy) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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
    
class LoginApi(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny, )
    @csrf_exempt
        
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                customer = serializer.validated_data['customer']
                
                token = generate_token(str(customer.id))
                
                user_data = {
                    "id": customer.id,
                    "first_name": customer.first_name,
                    "last_name":customer.last_name,
                    "email":customer.email,
                    "password":customer.password,
                    "area":customer.area.name,
                    "contact_no":customer.contact_no,
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


class ForgotPasswordApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            email = request.data['email']
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
            return Response({'result':True,
                             'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'result':False,
                            'message':'Please provide valid email address'},status=status.HTTP_400_BAD_REQUEST)


class OtpVerificationApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            customer_otp = request.data['otp']
            try:
                if customer_otp == str(request.session.get('otp')):
                    del request.session['otp']
                    reset_password_link = request.build_absolute_uri(reverse('reset_password'))

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
        

class DashboardPropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        try:
            state = request.query_params.get('state', None)
            city = request.query_params.get('city', None)
            area = request.query_params.get('area', None)
            
    
            
            if area:
                try:
                    area_obj = Area.objects.get(id=area)
                    properties = Properties.objects.filter(area_id=area_obj)
                except Area.DoesNotExist:
                    return Response({"result": False,
                                     "message": "No area found"},
                                    status=status.HTTP_404_NOT_FOUND)
            
            elif city:
                try:
                    city_obj = City.objects.get(id=city)
                    properties = Properties.objects.filter(area_id__city=city_obj)
                except City.DoesNotExist:
                    return Response({"result": False,
                                     "message": "No city found"},
                                    status=status.HTTP_404_NOT_FOUND)

            elif state:
                try:
                    state_obj = State.objects.get(id=state)
                    properties = Properties.objects.filter(area_id__city__state=state_obj)
                except State.DoesNotExist:
                    return Response({"result": False,
                                     "message": "No state found"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                properties = Properties.objects.all()
            
            serializer = DashboardPropertiesSerializer(properties, many=True)
            return Response({"result":True,
                            "data":serializer.data,
                            "message":"Property found successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message": "Error in getting data"}, status=status.HTTP_404_NOT_FOUND)



class CustomerProfileApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated, )
   
    
    def get(self,request):
        try:
            serializer = CustomerProfileSerializer(request.user)
    
            return Response({"result":True,
                            "data":serializer.data,
                            "message":"Customer found successfully"}, status=status.HTTP_200_OK)
                   
        except:
            return Response({"result":False,
                            "message": "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        

    def put(self, request):
        try: 
            serializer = CustomerProfileSerializer(request.user, data=request.data, partial=True)
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
 

class PropertyDetailApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
   
    def get(self, request, id):
        try:
            properties = Properties.objects.get(id=id)
            serializer = PropertiesDetailSerializer(properties)
            return Response({'result':True,
                            'data':serializer.data,
                            "message":"property found successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message":"Property not available"}, status=status.HTTP_400_BAD_REQUEST)  
    


class BookPropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            user = request.user
            bookings = Bookings.objects.filter(customer=user)
            serializer = BookPropertySerializer(bookings, many=True)
            return Response({
                'result': True,
                'data': serializer.data,
                'message': 'Booking history'
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'result': False,
                'message': 'History not available'
            }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id):
        try:
            user = request.user
            data = request.data.copy()
            data['customer'] = user.id

            serializer = BookPropertySerializer(data=data)
            if serializer.is_valid():
                property = Properties.objects.get(id=id)

                if property.status == 'inactive':
                    return Response({
                        'result': False,
                        'message': 'Property is already booked'
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer.validated_data['start_date'] = data.get('start_date')
                serializer.validated_data['end_date'] = data.get('end_date')
                serializer.validated_data['property'] = property

                serializer.save()

                # Change property status to "inactive"
                property.status = 'inactive'
                property.save()

                return Response({
                    'result': True,
                    'data': serializer.data,
                    'message': 'Property is booked'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'result': False,
                    'message': 'Property is not booked yet',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                'result': False,
                'message': 'Error in property booking'
            }, status=status.HTTP_400_BAD_REQUEST)      

class wishlistApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:   
            user = request.user
            wishlist = Wishlist.objects.filter(customer=user)
            serializer = WishlistSerializer(wishlist, many=True)
            return Response({'result': True,
                                    'data': serializer.data,
                                    'message': 'List of favourite properties'},
                                    status=status.HTTP_200_OK)
        except:
            return Response({'result': False,
                             'message': 'Error in property wishlist'},
                            status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, id):
        try:
            property = Properties.objects.get(id=id)
            user = request.user
            data = {
                'property': property.id,
                'customer': user.id
            }
            serializer = WishlistSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'result': True,
                                    'data': serializer.data,
                                    'message': 'Property is now favourite'},
                                    status=status.HTTP_200_OK)
            else:
                return Response({'result': False,
                                'message': 'Property is not favourited yet',
                                'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({'result': False,
                             'message': 'Error in property wishlist'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            wishlist = Wishlist.objects.get(id=id)
            wishlist.delete()
            return Response({'result': True,
                        'message': 'removed from wishlist'},
                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'result': False,
                        'message': 'Error in property remove'},
                        status=status.HTTP_400_BAD_REQUEST)