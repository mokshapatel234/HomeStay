from rest_framework import serializers 
from superadmin.models import City, State, Area


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
