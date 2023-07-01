from rest_framework import serializers 
from superadmin.models import Customer, Area, City, State, Properties, PropertyImage, PropertyTerms,\
      PropertyVideo, Bookings
from django.core.validators import RegexValidator
from .utils import generate_token



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

    def create(self, validated_data):
        user = Customer.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            area=validated_data['area'],
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

        attrs['customer'] = customer
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ['id','name']

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['id','name']


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ['id','name']


class DashboardPropertiesSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = Properties
        fields = ['name', 'root_image', 'price', 'status']



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


class PropertiesDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True)
    videos = PropertyVideoSerializer(many=True)
    terms = PropertyTermsSerializer(many=True)

    class Meta:
        model = Properties
        fields = ['name', 'root_image', 'price', 'status', 'description', 'area_id', 'address', 'images', 'videos', 'terms']



class BookPropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookings
        fields = ['id', 'customer', 'status', 'rent', 'transaction_id', 'start_date', 'end_date']
    