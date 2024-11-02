from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('register/', views.Registration, name='register'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard')
]