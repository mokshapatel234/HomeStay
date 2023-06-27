from rest_framework import serializers 
from superadmin.models import Customer, Area, City, State, Properties


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id','first_name', 'last_name', 'email', 'password', 'area','contact_no']



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
                customer = Customer.objects.get(email=email)

            except Customer.DoesNotExist:
                msg = {'detail': 'Customer is not registered.'}
                raise serializers.ValidationError(msg)

            if customer.password != password:
                msg = {'detail': 'Customer password is incorrect.'}
                raise serializers.ValidationError(msg)

        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['customer'] = customer
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ['id','name', 'city']

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['id','name', 'state']


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ['id','name']


class PropertiesSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = Properties
        fields = ['id', 'name', 'root_image', 'price', 'description', 'address', 'status', 'created_at', 'updated_at']

