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
from django.urls import path
from .views import selection_list, update_status, selection_create, selection_edit,selection_delete

urlpatterns = [
    path('', selection_list, name='selection_list'),
    path('update_status/<int:pk>/', update_status, name='update_status'),
    path('create/', selection_create, name='selection_create'),
    path('edit/<int:pk>/', selection_edit, name='selection_edit'),
    path('delete/<int:pk>/', selection_delete, name='selection_delete'),  # 削除URL
]

