from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'video').order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ['user__username', 'video__title', 'comment']

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter by video id
        video_id = self.request.query_params.get('video')
        if video_id:
            qs = qs.filter(video_id=video_id)
        # Non-admin users only see approved reviews
        user = self.request.user
        if not user.is_authenticated or not user.is_staff:
            qs = qs.filter(is_approved=True)
        return qs

    def perform_create(self, serializer):
        # Auto-set user to current user, is_approved defaults to False
        serializer.save(user=self.request.user, is_approved=False)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Admin approves a review"""
        if not request.user.is_staff:
            return Response({'detail': '权限不足'}, status=403)
        review = self.get_object()
        review.is_approved = True
        review.save(update_fields=['is_approved'])
        return Response(ReviewSerializer(review).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """Admin rejects a review"""
        if not request.user.is_staff:
            return Response({'detail': '权限不足'}, status=403)
        review = self.get_object()
        review.is_approved = False
        review.save(update_fields=['is_approved'])
        return Response(ReviewSerializer(review).data)
