from rest_framework import serializers

from .models import Building, School


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class SchoolSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = School
        fields = ['id', 'name', 'building', 'building_name', 'created_at']
        read_only_fields = ['id', 'created_at']
