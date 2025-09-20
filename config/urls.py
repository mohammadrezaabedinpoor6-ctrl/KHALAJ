"""config URL Configuration

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
from django.urls import path, include
# from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler403, handler400, handler500
from django.urls import path
from django.shortcuts import render

# تعریف handler برای ارورهای مختلف
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def custom_400(request, exception):
    return render(request, '400.html', status=400)

def custom_500(request):
    return render(request, '500.html', status=500)

# تعریف handler‌ها در urls.py
handler404 = custom_404
handler403 = custom_403
handler400 = custom_400
handler500 = custom_500


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', lambda request: render(request, "home.html" ), name='home'),
    path('', include('pages.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('khalaj/', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
