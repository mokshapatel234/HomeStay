from rest_framework import serializers 
from superadmin.models import Client, Properties, PropertyImage, PropertyVideo

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'profile_image', 'contact_no')

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
        fields = ('id', 'image')

class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ('id', 'video')

class PropertiesSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True)
    videos = PropertyVideoSerializer(many=True)

    class Meta:
        model = Properties
        fields = ('id', 'name', 'root_image', 'price', 'description', 'address', 'status', 'created_at', 'updated_at', 'deleted_at', 'images', 'videos')


class ClientProfileSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Client
        fields = ('username', 'first_name', 'last_name', 'profile_image', 'contact_no')
