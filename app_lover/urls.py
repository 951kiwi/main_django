"""
URL configuration for minecraft project.

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
from django.urls import path
from .views import phone_view,phone_name_birthday,get_data,PC_view,phone_data_save,Q3_QR,video_list

urlpatterns = [
    path('phone/', phone_view, name='phone'),
    path('PC_view/',PC_view,name="PC_view"),
    path('tiktok/', video_list, name='tiktok'),

    #データ変更用
    path('phone_name_birthday/',phone_name_birthday, name='phone_name_birthday'),   
    path('phone_data_save/',phone_data_save,name="phone_data_save"),
    path('get_data/',get_data,name="get_data"),
    path('Q3_QRload',Q3_QR,name="Q3_QRload"),
]
