"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from lidz.views import *

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('clients/', get_clients),
    path('clients/<int:client_id>/', get_client),
    path('clients-to-do-follow-up/', get_clients_last_message),
    path('client/', create_client),
    path('clients/<int:client_id>/score/', get_score),
]
