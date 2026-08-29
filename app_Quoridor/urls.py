from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<uuid:room_id>/', views.game_room, name='game_room'),
    path('api/room/<uuid:room_id>/move/', views.api_move_pawn, name='api_move'),
    path('api/room/<uuid:room_id>/fence/', views.api_place_fence, name='api_fence'),
    path('api/room/<uuid:room_id>/reset/', views.api_reset_game, name='api_reset'), # ★追加
]