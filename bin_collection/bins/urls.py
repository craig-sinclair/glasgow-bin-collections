from bins import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('select/', views.address_select, name='address_select'),
]
