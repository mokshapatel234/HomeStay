from rest_framework import serializers 
from superadmin.models import Client, Properties, PropertyImage, PropertyVideo,\
      Area, PropertyTerms, Bookings, TermsandPolicy, Customer
from django.core.validators import RegexValidator
from .utils import generate_token
from .models import ClientBanking
from django.conf import settings


class TermsAndPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsandPolicy
        fields = ['id', 'user', 'terms_and_condition', 'privacy_policy']


class RegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    contact_no = serializers.CharField(validators=[RegexValidator(regex=r"^\+?1?\d{10}$")])

    def validate(self, attrs):
        email = attrs.get('email')
        contact_no = attrs.get('contact_no')

        if Client.objects.filter(email=email).exists() and Client.objects.filter(contact_no=contact_no).exists():
            raise serializers.ValidationError("Email and Contact number already exist.")

        if Client.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")

        if Client.objects.filter(contact_no=contact_no).exists():
            raise serializers.ValidationError("Contact number already exists.")

        return attrs
   
    def create(self, validated_data):
        user = Client.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            area=validated_data['area'],
            password=validated_data['password'],
            contact_no=validated_data['contact_no']
        )
        token = generate_token(str(user.id))
        user.token = token.decode("utf-8")
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        client = None

        if email and password:
            try:
                client = Client.objects.get(email=email)

            except Client.DoesNotExist:
                msg = {'detail': 'Client is not registered.'}
                raise serializers.ValidationError(msg)

            if client.password != password:
                msg = {'detail': 'Client password is incorrect.'}
                raise serializers.ValidationError(msg)

        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['client'] = client
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)




class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id','image']

class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id','video']
class PropertyTermsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PropertyTerms
        fields = ['id', 'terms']

class PropertiesSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    terms = serializers.SerializerMethodField()

    def get_images(self, obj):
        image_urls = [image.image.url for image in obj.images.all()]
        return image_urls

    def get_videos(self, obj):
        video_urls = [video.video.url for video in obj.videos.all()]
        return video_urls

    def get_terms(self, obj):
        terms = [term.terms for term in obj.terms.all()]
        return terms

    class Meta:
        model = Properties
        fields = ['id', 'name', 'root_image', 'price', 'description', 'address', 'status', 'area_id', 'images', 'videos', 'terms']

class PropertiesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Properties
        fields = ['name', 'price', 'description', 'address', 'status', 'area_id']


class PropertiesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Properties
        fields = ['id', 'root_image', 'name', 'price','address', 'status']


class ClientProfileSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'profile_image', 'contact_no']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name','profile_image', 'contact_no', 'email']


class BookPropertySerializer(serializers.ModelSerializer):
    property_root_image = serializers.SerializerMethodField()
    customer_profile_image = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    property_name = serializers.SerializerMethodField()

    def get_property_root_image(self, obj):
        return obj.property.root_image.url if obj.property.root_image else None

    def get_customer_profile_image(self, obj):
        return obj.customer.profile_image.url if obj.customer.profile_image else None
    
    def get_customer_name(self, obj):
        return obj.customer.first_name if obj.customer else None

    def get_property_name(self, obj):
        return obj.property.name if obj.property else None

    class Meta:
        model = Bookings
        fields = ['id', 'property_name', 'property_root_image', 'customer_name', 'customer_profile_image', 'status', 'rent', 'start_date', 'end_date'] 
  

class BookingDetailSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Bookings
        fields = ['id', 'status', 'rent', 'start_date', 'end_date']


class ClientBankingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientBanking
        fields = ['account_number', 'bank_name', 'branch','ifsc_code', 'status']
    
    # def create(self, validated_data):
    #     # Retrieve banking details
    #     account_number = validated_data['account_number']
    #     bank_name = validated_data['bank_name']
    #     branch = validated_data['branch']
    #     ifsc_code = validated_data['ifsc_code']

    #     # Create the route in Razorpay
    #     client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    #     data = {
    #         'account_number': account_number,
    #         'bank_name': bank_name,
    #         'branch': branch,
    #         'ifsc_code': ifsc_code,
    #         'fund_account_id': '<your_fund_account_id>',
    #         'client_share': 80,
    #         # Additional route data as required
    #     }
    #     route = client.route.create(data=data)

    #     # Save the route details in your database
    #     validated_data['route_id'] = route['id']
    #     validated_data['recipient_id'] = route['recipient_id']

    #     return super().create(validated_data)

    def validate(self, attrs):
        account_number = attrs.get('account_number')
        ifsc_code = attrs.get('ifsc_code')
        
        if ClientBanking.objects.filter(account_number=account_number).exists() and ClientBanking.objects.filter(ifsc_code=ifsc_code).exists():
            raise serializers.ValidationError("Account number and ifsc_code number already exist.")

        if ClientBanking.objects.filter(account_number=account_number).exists():
            raise serializers.ValidationError("Account number already exists.")

        if ClientBanking.objects.filter(ifsc_code=ifsc_code).exists():
            raise serializers.ValidationError("IFSC code number already exists.")

        return attrs