from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status, generics
from django.template.loader import render_to_string
from rest_framework.response import Response
import random
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from superadmin.models import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from userapi.serializers import BookPropertyListSerializer, RegisterSerializer, LoginSerializer, ResetPasswordSerializer,\
      DashboardPropertiesSerializer,\
          CustomerProfileSerializer, PropertiesDetailSerializer, BookPropertySerializer,\
              TermsAndPolicySerializer, WishlistSerializer
from .utils import generate_token,get_transfers
from django.views.decorators.csrf import csrf_exempt
from .authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
import razorpay
from .models import BookProperty
from clientapi.models import ClientBanking
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
                request.session['customer'] = str(customer.id)
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
            email_errors = serializer.errors.get('email', [])
            password_errors = serializer.errors.get('password', [])
            
            error_messages = []
            if email_errors and password_errors:
                error_messages.append('Please provide email and password')


            elif email_errors:
                error_messages.append('Please provide email')
            elif password_errors:
                error_messages.append('Please provide password')
            


            if error_messages:
                response = Response({
                    "result": False,
                    "message": ', '.join(error_messages)
                }, status=status.HTTP_400_BAD_REQUEST)
                return response

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
            otp_string = str(generated_otp)            # otp_verification_link = request.build_absolute_uri(reverse('otpverify'))
            request.session['customer'] = str(customer_obj.id)
            request.session['otp'] = otp_string
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


class ChangePasswordApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        try:
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if not current_password or not new_password or not confirm_password:
                return Response({
                    "result": False,
                    "message": "Please provide the current password, new password, and confirm password."
                }, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_password:
                return Response({
                    "result": False,
                    "message": "New password and confirm password do not match."
                }, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            if current_password != user.password:
                return Response({
                    "result": False,
                    "message": "Current password is incorrect."
                }, status=status.HTTP_400_BAD_REQUEST)

            user.password=new_password
            user.save()

            # Ensure the user stays logged in by updating the session
            update_session_auth_hash(request, user)

            return Response({
                "result": True,
                "message": "Password changed successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "result": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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
    


class wishlistApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            user = request.user
            wishlist = Wishlist.objects.filter(customer=user)
            wishlist_serializer = WishlistSerializer(wishlist, many=True)


            return Response({'result': True,
                            'data': wishlist_serializer.data,
                            'message': 'List of favorite properties'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'result': False,
                            'message': 'Error in property wishlist',
                         'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        try:
            property_id = request.data.get('property_id')
            property = Properties.objects.get(id=property_id)
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
                                'message': 'Property is now favorite'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'result': False,
                                'message': 'Property is not favorited yet',
                                'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

        except Properties.DoesNotExist:
            return Response({'result': False,
                            'message': 'Invalid property ID'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'result': False,
                            'message': 'Error in property wishlist',
                            'error': str(e)},
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

class BookPropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            user = request.user
            bookings = BookProperty.objects.filter(customer=user) 
            serializer = BookPropertyListSerializer(bookings, many=True)

            data = []
            for booking in bookings:
                property_id = booking.property_id
                property_name = Properties.objects.get(id=property_id).name
                property_image = Properties.objects.get(id=property_id).root_image.url
                payment_status = 'Paid'  

                item = {
                    'property_name': property_name,
                    'root_image': property_image,
                    'payment_status': payment_status,
                    'start_date': booking.start_date,
                    'end_date': booking.end_date,
                    'amount': booking.amount
                }
                data.append(item)

            return Response({
                'result': True,
                'data': data,
                'message': 'Booking history'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'result': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, id):
        try:
            property = get_object_or_404(Properties, id=id)
            serializer = BookPropertySerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data

                validated_data['property'] = property
                validated_data['customer'] = request.user
                validated_data['currency'] = 'INR'

                instance = serializer.save()

                
                client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
                order_data = {
                    "amount": instance.amount*100,
                    "transfers":get_transfers(validated_data),
                    "currency":'INR'
                }
                print("instance amount", instance.amount)
    
                order = client.order.create(order_data)
                order_id = order.get('id', '')
                # Update the order_id in the serializer
                instance.order_id = order['id']
                instance.save()
    
                # print(serializer.data,"dataa")
                response_data = {
                    'result': True,
                    'data': serializer.data,
                    'message': 'Property is booked',
                    'order_id': order_id
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'result': False,
                    'message': 'Property is not booked yet',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'result': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


   

class VerifyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        try:
            order_id = request.data.get('order_id')
            status_value = request.data.get('status')

            if not order_id or status_value is None:
                return Response({
                    'result': False,
                    'message': 'order_id and status are required fields'
                }, status=status.HTTP_400_BAD_REQUEST)

            booking = BookProperty.objects.get(order_id=order_id)
            booking.status = status_value
            booking.save()


            return Response({
                'result': True,
                'message': f"Order {order_id} status updated successfully"
            }, status=status.HTTP_200_OK)
        except BookProperty.DoesNotExist:
            return Response({
                'result': False,
                'message': f"Order {order_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'result': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)