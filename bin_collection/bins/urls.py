from bins import views
from django.contrib import admin
from django.urls import path

app_name = 'bins'
urlpatterns = [
    path('', views.index, name='index'),
    path('select/', views.address_select, name='address_select'),
    path('about/', views.about, name='about'),
    path('check-driver-status/', views.check_driver_status, name='check_driver_status'), 
]
