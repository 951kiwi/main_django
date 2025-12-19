"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include,path
from app_Xmas.views import pc_view,quiz_view,join_view,player_logout_view,adminpage,pc_state_api,surprisebox_view,main_page

app_name = "Xmas"   # ← ★これが必要

urlpatterns = [
    path('main/', main_page, name='main'),
    path('join/', join_view, name='join'),
    path('Xmaslogout/', player_logout_view, name='Xmaslogout'),  # ←追加
    path("pc/", pc_view, name="pc"),
    path("quiz/", quiz_view, name="quiz"),
    path("admin/", adminpage, name="admin"),
    path("surprisebox/<str:name>/", surprisebox_view, name="surprisebox"),
    path("api/state/", pc_state_api, name="pc_state_api"),
]