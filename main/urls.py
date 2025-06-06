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
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , include('app_main.urls')),
    path('dareyaomae/' ,include('app_dareyaomae.urls')),
    path('minecraft/' ,include('app_minecraft.urls')),
    path('lover/',include('app_lover.urls')),
    path('FamilyCar/',include('app_FamilyCar.urls')),
    path('worker/',include('app_worker.urls')),
    path('anime/',include('app_anime.urls')),
    path('fileuploader/',include('app_fileuploader.urls')),
    # robots.txt
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain'), name="robots.txt"),
    
]

# DEBUG モードのときだけメディアファイルを提供
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)