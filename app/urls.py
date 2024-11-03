from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('register/', views.Registration, name='register'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add/', views.add_property, name='add_property'),
    path('update/<int:property_id>/', views.update_property, name='update_property'),

    path('property/', views.Properties, name='allproperties'),
    path('property/<int:property_id>', views.property_detail, name='property_detail'),
    path('book/<int:property_id>/', views.book_property, name='book_property'),
    path('seller/bookings/', views.seller_bookings, name='seller_bookings'),
    
]