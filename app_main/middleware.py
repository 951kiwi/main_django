# userlog/middleware.py

from .models import UserActivityLog
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin


class UpdateLastActivityMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            # 一定時間（例：1分）おきに更新
            last_activity = request.user.last_activity
            if not last_activity or (now() - last_activity).seconds > 60:
                request.user.last_activity = now()
                request.user.save(update_fields=['last_activity'])
        return None
    
class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith('/admin') or request.path.startswith('/static') or request.path.startswith('/media'):
            return response  # 管理画面や静的ファイルはスキップ

        user = request.user if request.user.is_authenticated else None
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')

        # DBに保存
        UserActivityLog.objects.create(
            user=user,
            path=request.path,
            method=request.method,
            ip_address=ip,
            user_agent=ua,
        )

        return response
