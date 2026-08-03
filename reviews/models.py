from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Review(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews', verbose_name=_('用户'))
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='reviews', verbose_name=_('视频'))
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('评分'),
    )
    comment = models.TextField(blank=True, verbose_name=_('评论'))
    is_approved = models.BooleanField(default=False, verbose_name=_('已审核'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))

    class Meta:
        verbose_name=_('评价')
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'video'], name='unique_user_video_review'),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.video.title}'