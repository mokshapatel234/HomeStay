from rest_framework import serializers 
from superadmin.models import Client, Properties, PropertyImage, PropertyVideo, Area
from django.core.validators import RegexValidator
from .utils import generate_token

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
        fields = ['id', 'image']

class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id', 'video']

class PropertiesSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = Properties
        fields = ['id', 'name', 'root_image', 'price', 'description', 'address', 'status', 'images', 'videos']


    
    
    

class ClientProfileSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'profile_image', 'contact_no']
