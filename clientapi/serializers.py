from rest_framework import serializers 
from superadmin.models import Client, Properties, PropertyImage, PropertyVideo,\
      Area, PropertyTerms, Bookings, TermsandPolicy, Customer
from django.core.validators import RegexValidator
from .utils import generate_token
from .models import ClientBanking, ClientNotification
from django.conf import settings
import razorpay
from userapi.models import BookProperty

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
    borded = serializers.BooleanField(default=False)
    otp_verified = serializers.BooleanField(default=False)

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

        if not email and not password:
            raise serializers.ValidationError(
                {'detail': 'Please provide "email" or "password".'},
                code='authorization'
            )
        elif email and not password:
            raise serializers.ValidationError(
                {'password': 'Please provide a password.'}
            )
        elif not email and password:
            raise serializers.ValidationError(
                {'email': 'Please provide an email.'}
            )

        if email and password:
            try:
                client = Client.objects.get(email=email)

            except Client.DoesNotExist:
                msg = {'detail': 'Client is not registered.'}
                raise serializers.ValidationError(msg)

            if client.password != password:
                msg = {'detail': 'Client password is incorrect.'}
                raise serializers.ValidationError(msg)

        
        
        attrs['client'] = client
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)





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

class PropertiesSerializer(DynamicFieldsModelSerializer):
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
        fields = ['name', 'root_image', 'price', 'description', 'address', 'status', 'area_id']


class PropertiesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Properties
        fields = ['id', 'root_image', 'name', 'price','address', 'status']

class PropertiesDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True)
    videos = PropertyVideoSerializer(many=True)
    terms = PropertyTermsSerializer(many=True)

    class Meta:
        model = Properties
        fields = ['name', 'root_image', 'price', 'status', 'description', 'area_id', 'address', 'images', 'videos', 'terms']



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
        model = BookProperty
        fields = ['id', 'property_name', 'property_root_image', 'customer_name', 'customer_profile_image','book_status', 'amount', 'start_date', 'end_date'] 
  

class BookingDetailSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = BookProperty
        fields = ['id', 'amount', 'start_date', 'end_date']


class ClientBankingSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    phone = serializers.CharField()
    contact_name = serializers.CharField()
    legal_business_name = serializers.CharField()
    business_type = serializers.CharField(required=False)  # Set as optional field
    type = serializers.CharField(required=False)  # Set as optional field

    class Meta:
        model = ClientBanking
        fields = ['email', 'phone', 'contact_name', 'legal_business_name', 'business_type', 'type']   



class AddressSerializer(serializers.Serializer):
    street1 = serializers.CharField()
    street2 = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    postal_code = serializers.CharField()
    country = serializers.CharField()

class ProfileSerializer(serializers.Serializer):
    category = serializers.CharField()
    subcategory = serializers.CharField()
    addresses = AddressSerializer()

class CustomClientBankingSerializer(ClientBankingSerializer):
    profile = ProfileSerializer()
    def get_default_type(self):
        return 'route'

    def get_default_business_type(self):
        return 'partnership'

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        internal_value['type'] = self.get_default_type()
        internal_value['business_type'] = self.get_default_business_type()

        profile_data = data.get('profile')
        if profile_data:
            internal_value['profile'] = self.fields['profile'].to_internal_value(profile_data)

        return internal_value
    

class SettlementSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    ifsc_code = serializers.CharField()
    beneficiary_name = serializers.CharField()

class PatchRequestSerializer(serializers.Serializer):
    settlements = SettlementSerializer()
    tnc_accepted = serializers.BooleanField()


class ClientNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientNotification
        fields = ['message']