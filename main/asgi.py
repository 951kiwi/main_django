# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

# 設定ファイルの環境変数をセット
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

# アプリケーションのルーティング
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTPリクエストは通常のDjango処理
    "websocket": AuthMiddlewareStack(  # WebSocketのルーティング
    ),
})
