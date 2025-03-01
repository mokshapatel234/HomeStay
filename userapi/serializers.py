from rest_framework import serializers
from clientapi.models import ClientBanking 
from superadmin.models import Customer, Area, City, State, Properties, PropertyImage, PropertyTerms,\
      PropertyVideo, Bookings, TermsandPolicy, Wishlist, Commission, Client
from django.core.validators import RegexValidator
from .utils import generate_token
from .models import BookProperty


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Customer
#         fields = ['id','first_name', 'last_name', 'email', 'password', 'area','contact_no']


class RegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    contact_no = serializers.CharField(validators=[RegexValidator(regex=r"^\+?1?\d{10}$")])
    token = serializers.CharField(max_length=255, read_only=True)
    fcm_token = serializers.CharField(max_length=255)
    
    def validate(self, attrs):
        email = attrs.get('email')
        contact_no = attrs.get('contact_no')

        if Customer.objects.filter(email=email).exists() and Customer.objects.filter(contact_no=contact_no).exists():
            raise serializers.ValidationError("Email and Contact number already exist.")

        if Customer.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")

        if Customer.objects.filter(contact_no=contact_no).exists():
            raise serializers.ValidationError("Contact number already exists.")

        return attrs

    def create(self, validated_data):
        user = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            area=validated_data['area'],
            contact_no=validated_data['contact_no'],
            fcm_token=validated_data['fcm_token']
        )
        token = generate_token(str(user.id))
        user.token = token.decode("utf-8")
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)
    fcm_token = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        fcm_token=attrs.get('fcm_token')
       
        customer = None

        if email and password:
            try:
                customer = Customer.objects.get(email=email)

            except Customer.DoesNotExist:
                message = {'detail': 'Customer is not registered.'}
                raise serializers.ValidationError(message)

            if customer.password != password:
                message = {'detail': 'Customer password is incorrect.'}
                raise serializers.ValidationError(message)

        else:
            message = 'Must include "email" and "password".'
            raise serializers.ValidationError(message, code='authorization')
        
        if fcm_token:
            try:
                
                customer = Customer.objects.get(email=email)
                # Check if there is an existing FCM token associated with the customer
                existing_fcm_token = customer.fcm_token
               
                
                if existing_fcm_token:
                    customer.fcm_token = fcm_token
                    customer.save()
            except Exception as e:
                print(str(e))

        attrs['customer'] = customer
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class CustomerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'password', 'email','profile_image', 'area','contact_no']



class PropertyImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image']

class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id', 'video']

class PropertyTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyTerms
        fields = ['id', 'terms'] 

class DashboardPropertiesSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_area(self, obj):
        return obj.area_id.name if obj.area_id else None
    def get_city(self, obj):
        return obj.area_id.city.name if obj.area_id.city else None
    def get_state(self, obj):
        return obj.area_id.city.state.name if obj.area_id.city.state else None
    
    def get_is_favourite(self, instance):
        return self.context['is_favourite'].get(instance.id, False)
    class Meta:
        model = Properties
        fields = ['id','name',  'price', 'status', 'root_image', 'area', 'city', 'state', 'is_favourite']

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     root_image = instance.root_image

        
    #     if root_image:
    #         root_image_data = {
    #             'id': instance.id,
    #             'image': root_image.url  
    #         }
    #         data['images'].insert(0, root_image_data)

    #     return data


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model= Client
        fields = ['id', 'first_name', 'last_name', 'profile_image', 'contact_no', 'email']

class PropertiesDetailSerializer(serializers.ModelSerializer):
    owner = ClientSerializer()
    images = PropertyImageSerializer(many=True)
    videos = PropertyVideoSerializer(many=True)
    terms = PropertyTermsSerializer(many=True)

    class Meta:
        model = Properties
        fields = ['name', 'price', 'status', 'description', 'area_id', 'address', 'root_image', 'images', 'videos', 'terms', 'owner']

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     root_image = instance.root_image

        
    #     if root_image:
    #         root_image_data = {
    #             'id': instance.id,
    #             'image': root_image.url  
    #         }
    #         data['images'].insert(0, root_image_data)

    #     return data


class BookPropertyListSerializer(serializers.ModelSerializer):
    property_root_image = serializers.SerializerMethodField()
    property_name = serializers.SerializerMethodField()
    
    def get_property_root_image(self, obj):
        return obj.property.root_image.url if obj.property.root_image else None

    def get_property_name(self, obj):
        return obj.property.name if obj.property else None

    class Meta:
        model = BookProperty
        fields = ('id','property_name', 'property_root_image', 'book_status','start_date', 'end_date', 'amount','order_id')
        


class TermsAndPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsandPolicy
        fields = ['id', 'user', 'terms_and_condition', 'privacy_policy']

class WishlistSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    root_image = serializers.ImageField(source='property.root_image', read_only=True)
    price = serializers.FloatField(source='property.price', read_only=True)
    status = serializers.CharField(source='property.status', read_only=True)
    area = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def get_area(self, obj):
        return obj.property.area_id.name if obj.property.area_id else None
    def get_city(self, obj):
        return obj.property.area_id.city.name if obj.property.area_id.city else None
    def get_state(self, obj):
        return obj.property.area_id.city.state.name if obj.property.area_id.city.state else None


    class Meta:
        model = Wishlist
        fields = ['id', 'property', 'property_name', 'customer', 'price', 'area', 'city', 'state', 'status',  'root_image']


    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     # Get the root image of the property related to the wishlist
    #     property_root_image = instance.property.root_image

    #     # If a root image exists, add it to the images list
    #     if property_root_image:
    #         root_image_data = {
    #             'id': instance.property.id,
    #             'image': property_root_image.url  # Assuming 'url' is the attribute for the image URL
    #         }
    #         data['images'].insert(0, root_image_data)

    #     return data
    







class BookPropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = BookProperty
        fields = ('id', 'book_status','start_date', 'end_date', 'amount')
        

   

