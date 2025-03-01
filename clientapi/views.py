from rest_framework import filters
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status, generics
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import serializers
from django.http import JsonResponse
import random
import requests
from userapi.models import BookProperty
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from superadmin.models import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from clientapi.serializers import PatchRequestSerializer, RegisterSerializer, LoginSerializer,\
      ResetPasswordSerializer, ClientProfileSerializer,PropertiesListSerializer, PropertiesSerializer,\
      BookPropertySerializer, TermsAndPolicySerializer, BookingDetailSerializer, CustomerSerializer, \
      ClientBankingSerializer, PropertiesUpdateSerializer, PropertiesDetailSerializer, ClientNotificationSerializer
from .utils import generate_token
from django.views.decorators.csrf import csrf_exempt
from .authentication import JWTAuthentication, IsClientVerified
from rest_framework.parsers import MultiPartParser
from .paginator import ClientPagination
from django.db.models import Q
import razorpay
from datetime import datetime
from django.utils import timezone
from .models import ClientBanking, Product, Otp, ClientNotification
from rest_framework.views import APIView


class TermsAndPolicyApi(generics.GenericAPIView):
    permission_classes =(permissions.AllowAny, )
    
    def get(self, request):
        terms_and_policy = TermsandPolicy.objects.first()  
        serializer = TermsAndPolicySerializer(terms_and_policy) 
        return Response(serializer.data, status=status.HTTP_200_OK)


class FirebaseApi(APIView):
     def post(self, request):
        try:
            email = request.data['email']
            if email:
                print(email)
            else:
                print("error")
            client_obj = Client.objects.get(email=email)
            otp_verified = request.data.get('otp_verified', None)
            if otp_verified is not None: 
                client_id = client_obj.id 
                try:
                    client = Client.objects.get(id=client_id)
                    client.otp_verified = bool(otp_verified) 
                    client.save()
                    return Response({'message': 'OTP verified status updated successfully.'}, status=status.HTTP_200_OK)
                except Client.DoesNotExist:
                    return Response({'message': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'No value provided for otp_verified.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Register Client
class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            serializer = self.serializer_class(data = request.data, context={'request': request})
        
            if serializer.is_valid():
                user = serializer.save()
                area = request.data.get('area')
                area = get_object_or_404(Area, id=area)
                city = area.city
                state = area.city.state
               
                token = generate_token(str(user.id))
                user_token = token.decode("utf-8")
                response_data = {
                    "result": True,
                    "data": {
                        **serializer.data,
                        "area": {
                            "area_id": area.id,
                            "area_name": area.name,
                            "city_id": city.id,
                            "city_name": city.name,
                            "state_id": state.id,
                            "statename": state.name
                        }
                    },
                    "token": user_token,
                    "message": "Customer created successfully",
                }
                
                response = Response(response_data, status=status.HTTP_201_CREATED)
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
                user_token = token.decode("utf-8")
                
                user_data = {
                    "id": client.id,
                    "first_name": client.first_name,
                    "last_name":client.last_name,
                    "email":client.email,
                    "password":client.password,
                    "contact_no":client.contact_no,
                    "borded":client.borded,
                    "otp_verified":client.otp_verified,
                    "area":{
                   
                        'area_name': client.area.name,
                        'area_id': client.area.id,
                        'city_name': client.area.city.name,
                        'city_id': client.area.city.id,
                        'state_name': client.area.city.state.name,
                        'state_id': client.area.city.state.id,
                    }
                    
                    
                }
                
                return Response({"result":True, 
                                    "data":user_data,
                                    "token":user_token,
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

            # Default error handling
            errors = [str(error[0]) for error in serializer.errors.values()]
            response = Response({
                "result": False,
                "message": ', '.join(errors)
            }, status=status.HTTP_400_BAD_REQUEST)
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
            otp_string = str(generated_otp)
            # otp_verification_link = request.build_absolute_uri(reverse('otpverify'))
            request.session['client'] = str(client_obj.id)
            otp_instance = Otp.objects.create(client=client_obj, otp=otp_string)
            print(type(otp_string))
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
        except Exception as e:
            return Response({'result':False,
                            'message':"Something went wrong"},status=status.HTTP_400_BAD_REQUEST)



# OTP Verification
class OtpVerificationApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self,request):
        try:
            client_otp = request.data['otp']
            otp = Otp.objects.filter(otp=client_otp).first()
            print(otp)
            try:
                if otp:
                    otp.is_verified = True
                    otp.save()

                    return Response({'result': True, 'message': 'Otp Verified'}, status=status.HTTP_200_OK)
                    
                else:
                    return Response({'result': False, 'message': 'No Otp Found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'result':False,
                                "message":"Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'result':False,
                            'message':"Something went wrong"},status=status.HTTP_404_NOT_FOUND)
     


# Reset Password
class ResetPasswordApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        try:
            email = request.data['email']
            client_obj = Client.objects.get(email=email)
            print(client_obj)
            try:
                otp = Otp.objects.get(client=client_obj.id)
            except Otp.DoesNotExist:
                return Response({'result': False, 'message': 'No OTP found for the client'}, status=status.HTTP_404_NOT_FOUND)
            if otp.is_verified:
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)

                new_password = serializer.validated_data['new_password']
                confirm_password = serializer.validated_data['confirm_password']
                if new_password == confirm_password:
                    client_obj = Client.objects.get(id=client_obj.id)
                    client_obj.password = new_password
                    client_obj.save()
                    otp.delete()
                    del request.session['client']

                    return Response({'result':True,
                                    'message':'Password Changed Successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'result':False,
                                    'message':'Password Not Matched'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'result':False,
                                'message':'Cannot Change Password Without otp verification '},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:

            return Response({'result':False,
                            'message':"Something went wrong"},status=status.HTTP_404_NOT_FOUND)


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
            serializer = ClientProfileSerializer(request.user, data=request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                client_instance = get_object_or_404(Client, id=request.user.id)
                noti_data = {
                    'client': client_instance,
                    'title': "About profile updation",
                    'message': "Profile updated successfully"
                }
                client_noti_obj = ClientNotification(**noti_data)
                client_noti_obj.save()
                return Response({"result":True,
                                "data":serializer.data,
                                'message':'Profile Updated'},status=status.HTTP_201_CREATED)
            else:
                return Response({"result":False,
                                "message": "Error in updating profile"}, status=status.HTTP_400_BAD_REQUEST)
       
        except Exception as e:
            return Response({"result":False,
                            "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
# Property Management

class PropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    parser_classes = (MultiPartParser, )
    pagination_class = ClientPagination
    # page_size = 5updateprofile
    # page = 1
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'address', 'price', 'status']  # Add the fields you want to search by

    def get(self, request):
        try:
            
            query = request.GET.get('query')  # Get the search query from the request
            properties = request.user.properties.all()

            if query:
                # Apply search filter using Q objects
                properties = properties.filter(
                    Q(name__icontains=query) |  
                    Q(address__icontains=query) |
                    Q(price__icontains=query) |
                    Q(status__icontains=query)  
                )

            serializer = PropertiesSerializer(properties, many=True)
            

            paginated_properties = self.paginate_queryset(properties)
            serializer = PropertiesSerializer(paginated_properties, many=True)
            response_data = serializer.data

        # Get the area, city, and state names for each property
            for property_data in response_data:
                area_id = property_data['area_id']
                area = Area.objects.filter(id=area_id).first()
                if area:
                    city = area.city
                    state = city.state
                    property_data['area'] = {
                        'area_name': area.name,
                        'area_id': area.id,
                        'city_name': city.name,
                        'city_id': city.id,
                        'state_name': state.name,
                        'state_id': state.id,
                    }

            return self.get_paginated_response(response_data)
        except:
            return Response({"result": False, "message": "Property not available"}, status=status.HTTP_400_BAD_REQUEST)

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
                client_instance = get_object_or_404(Client, id=request.user.id)
                noti_data = {
                    'client': client_instance,
                    'title' : "About Property",
                    'message': "Property added successfully"
                }
                client_noti_obj = ClientNotification(**noti_data)
                client_noti_obj.save()
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
            area = property_obj.area_id
            city = area.city
            state = city.state
         
            print(state.name, city.name, area.name)
            area_id = request.data.get('area_id')
            if area_id:
                area = get_object_or_404(Area, id=area_id)
                city = area.city
                state = city.state
          
                print(state.name, city.name, area.name)
            serializer = PropertiesUpdateSerializer(property_obj, data=request.data,  partial=True)

            if serializer.is_valid():
                serializer.save()

                images = request.FILES.getlist('images')
                
                if images:
                    property_obj.images.all().delete()
                    for image in images:
                        PropertyImage.objects.create(property=property_obj, image=image)

                videos = request.FILES.getlist('videos')
                if videos:
                    property_obj.videos.all().delete()
                    for video in videos:
                        PropertyVideo.objects.create(property=property_obj, video=video)


                terms = request.POST.get('terms')
                if terms:
                    property_obj.terms.all().delete()
                    PropertyTerms.objects.create(property=property_obj, terms=terms)

                updated_property_serializer = PropertiesSerializer(property_obj)
                updated_property_data = updated_property_serializer.data
                updated_property_data['area'] = {
                'name': area.name,
                'id':area.id,
                'city': city.name,
                'city_id':city.id,
                'state': state.name,
                'state_id':state.id,
            }

                client_instance = get_object_or_404(Client, id=request.user.id)
                noti_data = {
                    'client': client_instance,
                    'title' : "About Property",
                    'message': "Property updated successfully"
                }
                client_noti_obj = ClientNotification(**noti_data)
                client_noti_obj.save()


                return Response({
                    "result": True,
                    "data": updated_property_data,
                    "message": "Property updated successfully"
                }, status=status.HTTP_200_OK)
                
            else:
                return Response({
                    "result": False,
                    "message": 'Error in property updation'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "result": False,
                "message": "Something went wrong"
            }, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, property_id):
        try:
            property_instance = request.user.properties.get(id=property_id)
            property_instance.delete()
            return Response({'result':True,
                            "message":"property deleted successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"result":False,
                            "message":"Property not available"}, status=status.HTTP_400_BAD_REQUEST)  
    
class PropertyDetailApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
   
    def get(self, request, id):
        try:
            property = Properties.objects.get(id=id)
            serializer = PropertiesDetailSerializer(property)

            area = property.area_id
            city = area.city
            state = city.state

            response_data = serializer.data
            response_data['area'] = {
                'name': area.name,
                'id': area.id,
                'city': city.name,
                'city_id': city.id,
                'state': state.name,
                'state_id': state.id,
            }

            return Response({
                'result': True,
                'data': response_data,
                'message': 'Property found successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"result":False,
                            "message":"Property not found"}, status=status.HTTP_400_BAD_REQUEST)  
    



class DashboardApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )


    def get(self, request):
        try:
            user = request.user

            properties = user.properties.order_by('-created_at')[:10]
            bookings = BookProperty.objects.filter(property__owner=user,  book_status__in=[True]).order_by('-created_at')[:10]
            property_serializer = PropertiesSerializer(properties, many=True, fields = ['id', 'root_image', 'name', 'price','address', 'status'] )
            booking_serializer = BookPropertySerializer(bookings, many=True)
            
            data = {
                'properties': property_serializer.data,
                'bookings': booking_serializer.data,
                "id": user.id,
                "first_name": user.first_name,
                "last_name":user.last_name,
                "email":user.email,
                "password":user.password,
                "contact_no":user.contact_no,
            }
            if user.profile_image:
                data['profile_image'] = user.profile_image.url

            return Response({
                "result": True,
                "data": data,
                'message': 'Data found successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "result": False,
                "message":"Something went wrong"
            }, status=status.HTTP_400_BAD_REQUEST)

class CalenderApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            user = request.user
            current_date = timezone.now()

            requested_month = request.query_params.get('month', None)
            requested_year = request.query_params.get('year', None)
            
            if requested_year:
                try:
                    requested_year = int(requested_year)
                    if requested_year < 1:
                        raise ValueError("Invalid year value")
                except ValueError:
                    return Response({"error": "Invalid year value. Year must be a positive integer."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                requested_year = current_date.year

            if requested_month:
                try:
                    requested_month = int(requested_month)
                    if requested_month < 1 or requested_month > 12:
                        raise ValueError("Invalid month value")
                except ValueError:
                    return Response({"error": "Invalid month value. Month must be an integer between 1 and 12."},
                                    status=status.HTTP_400_BAD_REQUEST)

                start_date = timezone.datetime(requested_year, requested_month, 1)
                next_month = requested_month + 1 if requested_month < 12 else 1
                next_year = requested_year + 1 if requested_month == 12 else requested_year
                end_date = timezone.datetime(next_year, next_month, 1)


                bookings = BookProperty.objects.filter(
                    Q(start_date__gte=start_date, start_date__lt=end_date, property__owner=user, book_status__in=[True]) |
                    Q(end_date__gte=start_date, end_date__lt=end_date, property__owner=user, book_status__in=[True]) 
                ).order_by('start_date')
            else:
                current_date = timezone.now()
                start_date = timezone.datetime(current_date.year, current_date.month, 1)
                next_month = current_date.month + 1 if current_date.month < 12 else 1
                next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
                end_date = timezone.datetime(next_year, next_month, 1)

                bookings = BookProperty.objects.filter(
                    Q(start_date__gte=start_date, start_date__lt=end_date, property__owner=user, book_status__in=[True]) |
                    Q(end_date__gte=start_date, end_date__lt=end_date, property__owner=user, book_status__in=[True]) 
                ).order_by('start_date')

           
            serializer = BookPropertySerializer(bookings, many=True)
            if not serializer.data:  
                return Response({
                    'result': False,
                    'data': [],
                    'message': 'No bookings found for the specified month and year.'
                }, status=status.HTTP_200_OK)
            return Response({
                    'result': True,
                    'data': serializer.data,
                    'message': "Data found successfully"
                }, status=status.HTTP_200_OK)

            
        except Exception as e:
            print(e)
            return Response({"error": "An error in data foundation"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookPropertyApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = ClientPagination
  
    def get(self, request):
        try:
            user = request.user
            query = request.GET.get('query') 


            bookings = BookProperty.objects.filter(property__owner=user, book_status__in=[True])
            if query:
                bookings = bookings.filter(
                    Q(property__name__icontains=query) |
                    Q(customer__first_name__icontains=query) 
                  )
            page = self.paginate_queryset(bookings) 

            if page:

                serializer = BookPropertySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)  
            else:
                return Response({
                    'result': True,
                    'data': [],
                    'message': 'Empty booking history'
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'result': False,
                'message': "Something went wrong" 
            }, status=status.HTTP_400_BAD_REQUEST)

       
class BookingDetailApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, id):
        try:
            booking = BookProperty.objects.get(id=id)
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
                'message': 'Error in data found' },status=status.HTTP_400_BAD_REQUEST)  
    


class BankingAndProductApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            base_url = "https://api.razorpay.com/v2"
            endpoint = "/accounts"
            url = base_url + endpoint

            request.data['type'] = 'route'
            request.data['business_type'] = 'partnership'
            serializer = ClientBankingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            settlements_data = request.data.pop('settlements', {})
            tnc_accepted = request.data.pop('tnc_accepted', False)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic cnpwX3Rlc3RfVHk4OTBxY0M4NW5xNUk6ZVZ0M2xCdjAzSXJWa2k4ZEJrb1NucnNi'
            }

            response = requests.post(url, json=request.data, headers=headers)

            if response.status_code == 200:
                account_data = response.json()
                serializer.save(
                    client=request.user,
                    status='active',
                    account_id=account_data.get('id', ''),
                    type='route',
                    business_type='partnership'
                )

                product_data = {
                    "product_name": "route"
                }

                endpoint = f"/accounts/{account_data.get('id', '')}/products"
                url = base_url + endpoint

                response = requests.post(url, json=product_data, headers=headers)

                if response.status_code == 200:
                    product_data = response.json()
                    product_id = product_data.get("id")
                    product = Product(product_id=product_id)
                    product.save()

                    # Update bank details with patch method
                    endpoint = f"/accounts/{account_data.get('id', '')}/products/{product_id}/"
                    url = base_url + endpoint

                    # Create the payload for the patch request
                    patch_data = {
                        'settlements': settlements_data,
                        'tnc_accepted': tnc_accepted
                    }

                    serializer = PatchRequestSerializer(data=patch_data)
                    serializer.is_valid(raise_exception=True)

                    data = serializer.validated_data

                    product.settlements_account_number = data['settlements']['account_number']
                    product.settlements_ifsc_code = data['settlements']['ifsc_code']
                    product.settlements_beneficiary_name = data['settlements']['beneficiary_name']
                    product.tnc_accepted = data['tnc_accepted']
                    product.save()

                    response = requests.patch(url, json=patch_data, headers=headers)

                    if response.status_code == 200:
                        updated_product_data = response.json()

                        user = request.user
                        user.borded = True
                        user.save()
                        client_instance = get_object_or_404(Client, id=request.user.id)
                        noti_data = {
                            'client': client_instance,
                            'title' : "About Banking Detail",
                            'message': "Your banking detail added successfully."
                        }
                        client_noti_obj = ClientNotification(**noti_data)
                        client_noti_obj.save()
                        return Response({
                            "result": True,
                            "data": updated_product_data,
                            "borded":user.borded,
                            "otp_verified":user.otp_verified,
                            "message": "Product and bank details updated successfully",
                        }, status=status.HTTP_200_OK)

                    return Response({
                        "result": False,
                        "message": "Failed to update product and bank details in Razorpay",
                        "api_response": response.json()
                    }, status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    "result": False,
                    "message": "Failed to create product in Razorpay",
                    "api_response": response.json()
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "result": False,
                "message": "Failed to create account in Razorpay",
                "api_response": response.json()
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "result": False,
                "message": "Something went wrong"
            }, status=status.HTTP_400_BAD_REQUEST)


class ClientNotificationApi(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        try:
            notifications = ClientNotification.objects.filter(client=request.user)
            

            notification_serializer = ClientNotificationSerializer(notifications, many=True)
            

            
            return Response({'result':True,
                            'data':notification_serializer.data,
                            "message":"Notifications found successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'result': False,
                'message': str(e) },status=status.HTTP_400_BAD_REQUEST)  
    