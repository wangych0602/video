from rest_framework import serializers

from .models import LiveRoom


class LiveRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveRoom
        fields = [
            'id',
            'name',
            'school',
            'teacher',
            'status',
            'scheduled_at',
            'started_at',
            'ended_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
