"""raiseticket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from rts.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index,name="index"),
    path('createticket/',createticket,name="createticket"),
    path('deleteticket/<int:id>/',deleteticket,name="deleteticket"),
    path('editticket/<int:id>/',editticket,name="editticket"),
    path('contact/',contact,name="contact"),
    path('feedback/',feedback,name="feedback"),
    path('about/',about,name="about"),
    path('register/',register,name="register"),
    path('login/',login,name="login"),
    path('logouts/',logouts,name="logouts"),
    path('dashboard/',dashboard,name="dashboard"),
    path('search/',search,name="search"),
    path('ticket/<int:id>/<slug:slug>', post, name = 'post'),
    url('^', include('django.contrib.auth.urls')),
    path('activate/<uidb64>/<token>/',activate, name='activate'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Raise Ticket System"
admin.site.site_title = "Admin Area | RTS"
admin.site.index_title = "Admin Control | RTS"