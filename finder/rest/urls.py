from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views


urlpatterns = [
    path('get_accords', views.getAccords, name='get_accords'),
    path('get_notes', views.getNotes, name='get_notes'),
    path('get_olfactory_family', views.getOlfactory, name='get_accords'),

    # path('teste/', views.testAPI),
    # other paths...
]

