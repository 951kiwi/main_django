from django.urls import path
from . import views

app_name = "app_wifi"

urlpatterns = [
    path("", views.profile_list, name="profile_list"),
    path("create/", views.create_link, name="create_link"),
    path("disable/<int:pk>/", views.disable_link, name="disable_link"),
    path("download/<str:token>/", views.download_page, name="download_page"),
    path("file/<str:token>/", views.download_profile, name="download_profile"),
]
