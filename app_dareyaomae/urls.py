"""dareyaomae URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from app_dareyaomae.views import create_room,host_room,join_room,game_room,useto_card_room,set_name,set_drawn,get_card,test,startmenu,uploadImage,joinSerch_room,finish_room
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',startmenu,name="startmenu"),
    path('Serch/', joinSerch_room,name='joinSerch_room'),
    path('join/<int:room_id>/', join_room,name='join_room'),
    path('upload/<int:room_id>/', uploadImage, name='upload_images'),
    path('create/',create_room,name="create_room"),
    path('host/<int:room_id>/', host_room, name='host_room'),
    path('use_to/<int:room_id>/',useto_card_room,name='useto_card_room'),
    path('game_room/<int:room_id>/',game_room,name="game_room"),
    path('finish/<int:room_id>/',finish_room,name="finish"),
    path('test/',test,name="test"),
    #Ajax
    path('set_name/',set_name,name='set_name'),
    path('set_drawn/',set_drawn,name="set_drawn"),
    path('get_card/',get_card,name='get_card'),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
