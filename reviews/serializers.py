from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_username', 'user_first_name', 'video', 'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'is_approved', 'created_at']
