from django.contrib import admin
from django.urls import path
from bins import views
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bins/', include('bins.urls')),
]
