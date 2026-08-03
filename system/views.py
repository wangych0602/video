from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import subprocess
import os

from .models import SiteConfig


class SiteConfigView(APIView):
    """获取站点配置"""
    permission_classes = [AllowAny]

    def get(self, request):
        config, created = SiteConfig.objects.get_or_create(id=1)
        return Response({
            'site_name': config.site_name,
            'site_description': config.site_description,
            'default_language': config.default_language,
            'contact_email': config.contact_email,
            'registration_enabled': config.registration_enabled,
            'footer_text': config.footer_text,
            'footer_copyright': config.footer_copyright,
            'footer_icp': config.footer_icp,
        })


class AIHealthView(APIView):
    """AI 分析环境健康检查"""
    permission_classes = [AllowAny]

    def get(self, request):
        result = {
            'ffmpeg_status': 'unknown',
            'ffprobe_status': 'unknown',
            'redis_status': 'unknown',
            'celery_status': 'unknown',
            'api_key_status': 'unknown',
        }

        # 检查 ffmpeg
        try:
            result_ffmpeg = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result_ffmpeg.returncode == 0:
                result['ffmpeg_status'] = 'ok'
                first_line = result_ffmpeg.stdout.split('\n')[0] if result_ffmpeg.stdout else ''
                result['ffmpeg_version'] = first_line
            else:
                result['ffmpeg_status'] = 'error'
        except FileNotFoundError:
            result['ffmpeg_status'] = 'not_found'
        except Exception as e:
            result['ffmpeg_status'] = 'error'
            result['ffmpeg_error'] = str(e)

        # 检查 ffprobe
        try:
            result_ffprobe = subprocess.run(
                ['ffprobe', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result_ffprobe.returncode == 0:
                result['ffprobe_status'] = 'ok'
                first_line = result_ffprobe.stdout.split('\n')[0] if result_ffprobe.stdout else ''
                result['ffprobe_version'] = first_line
            else:
                result['ffprobe_status'] = 'error'
        except FileNotFoundError:
            result['ffprobe_status'] = 'not_found'
        except Exception as e:
            result['ffprobe_status'] = 'error'
            result['ffprobe_error'] = str(e)

        # 检查 Redis
        try:
            import redis
            redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
            r = redis.from_url(redis_url)
            r.ping()
            result['redis_status'] = 'ok'
        except ImportError:
            result['redis_status'] = 'redis_lib_not_found'
        except Exception as e:
            result['redis_status'] = 'error'
            result['redis_error'] = str(e)

        # 检查 Celery Worker
        try:
            from celery import current_app
            insp = current_app.control.inspect()
            ping_result = insp.ping()
            if ping_result:
                result['celery_status'] = 'ok'
                result['workers'] = list(ping_result.keys())
                result['celery_workers'] = len(ping_result)
            else:
                result['celery_status'] = 'no_workers'
                result['workers'] = []
                result['celery_workers'] = 0
        except Exception as e:
            result['celery_status'] = 'unknown'
            result['workers'] = []
            result['celery_error'] = str(e)

        # 检查 API Key 配置
        api_keys = []
        if os.environ.get('OPENAI_API_KEY'):
            api_keys.append('openai')
        if os.environ.get('GOOGLE_API_KEY'):
            api_keys.append('google')
        
        if api_keys:
            result['api_key_status'] = 'configured'
            result['configured_providers'] = api_keys
        else:
            result['api_key_status'] = 'not_configured'

        # 总体状态
        all_ok = (
            result['ffmpeg_status'] == 'ok' and
            result['ffprobe_status'] == 'ok' and
            result['redis_status'] == 'ok' and
            result['celery_status'] == 'ok' and
            result['api_key_status'] == 'configured'
        )
        result['overall_status'] = 'healthy' if all_ok else 'degraded'

        return Response(result)
