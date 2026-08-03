from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView

from django.db.models import Q

from .models import TeacherProfile
from .permissions import IsAdminUser
from .serializers import TeacherProfileSerializer, UserSerializer
from .serializers import TeacherDirectorySerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['username', 'email', 'first_name']


class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.select_related('user', 'school').order_by('id')
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['user__username', 'subject', 'school__name']

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取或更新当前登录教师的个人资料"""
        teacher = getattr(request.user, 'teacher_profile', None)
        if not teacher:
            return Response(
                {'detail': '当前用户不是教师，没有教师资料'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = self.get_serializer(teacher)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = self.get_serializer(teacher, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class TeacherListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        qs = TeacherProfile.objects.select_related('user', 'school').all()
        if q:
            qs = qs.filter(Q(user__username__icontains=q) | Q(subject__icontains=q) | Q(school__name__icontains=q))
        return Response(TeacherDirectorySerializer(qs[:50], many=True).data)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({'detail': '用户名或密码错误'}, status=400)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})
