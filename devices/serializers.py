from rest_framework import serializers

from .models import Device, LiveSession


class DeviceSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Device
        fields = [
            'id',
            'device_name',
            'device_sn',
            'device_type',
            'manufacturer',
            'model',
            'firmware_version',
            'school',
            'school_name',
            'location',
            'ip_address',
            'mac_address',
            'status',
            'last_online_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'last_online_time', 'created_at', 'updated_at']


class LiveSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveSession
        fields = [
            'id',
            'device',
            'title',
            'teacher',
            'school',
            'stream_key',
            'rtmp_push_url',
            'hls_url',
            'status',
            'created_time',
            'start_time',
            'end_time',
        ]
        read_only_fields = ['id', 'created_time']


class PublicLiveSessionSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = LiveSession
        fields = [
            'id',
            'device_name',
            'title',
            'school',
            'school_name',
            'hls_url',
            'status',
            'created_time',
            'start_time',
            'end_time',
        ]
        read_only_fields = fields
