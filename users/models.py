from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('管理员')
        SCHOOL_ADMIN = 'school_admin', _('学校管理员')
        TEACHER = 'teacher', _('教师')
        STUDENT = 'student', _('学生')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name=_('角色'))
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('所属学校'),
    )

    class Meta:
        verbose_name=_('用户')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', verbose_name=_('用户'))
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='teacher_profiles',
        verbose_name=_('学校'),
    )
    subject = models.CharField(max_length=100, blank=True, verbose_name=_('科目'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name=_('头像'))
    description = models.TextField(blank=True, verbose_name=_('简介'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))

    class Meta:
        verbose_name=_('教师资料')
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} - {self.school.name}'