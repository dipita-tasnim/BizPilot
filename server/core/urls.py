"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chat.views import chat_api, idea_ingest_api, pricing_tiers_api, feedback_api, file_upload_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/upload/', file_upload_api, name='file_upload_api'),
    path('api/idea/', idea_ingest_api, name='idea_ingest_api'),
    path('api/pricing/', pricing_tiers_api, name='pricing_tiers_api'),
    path('api/feedback/', feedback_api, name='feedback_api'),
    path('', include('main.urls')),  # Include main app URLs (this includes the landing page)
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
