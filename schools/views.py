from rest_framework import viewsets

from .models import Building, School
from .serializers import BuildingSerializer, SchoolSerializer
from users.permissions import IsPublicReadOrAdmin


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [IsPublicReadOrAdmin]
    search_fields = ['name', 'description']


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.select_related('building').all()
    serializer_class = SchoolSerializer
    permission_classes = [IsPublicReadOrAdmin]
    search_fields = ['name', 'building__name']
