from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views


urlpatterns = [
    
    path('brands', views.get_brands, name='brands'),
    path('get_details', views.getDetails, name='get_details'),

    # path('teste/', views.testAPI),
    # other paths...
]

