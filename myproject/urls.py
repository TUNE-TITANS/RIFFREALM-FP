"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# urls.py

from django.urls import path
from myapp import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    path('library', views.library, name='library'),
    path('search/', views.search, name='search'),
    path('signout/', views.signout, name='signout'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path('recommendation/', views.recommendation, name='recommendation'),
    path('songs/', views.songs, name='songs'),
    
]