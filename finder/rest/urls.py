from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views


urlpatterns = [
    path('get_data', views.get_data, name='get_data'),
    path('get_info', views.getInfo, name='get_info'),
    path('get_reactions', views.getReactions, name='get_reactions'),
    path('get_details', views.getDetails, name='get_details'),
    path('get_notes', views.getNotes, name='get_notes'),
    path('get_olfactory_family', views.getOlfactory, name='get_accords'),
    path('brands', views.get_brands, name='brands'),

    # path('teste/', views.testAPI),
    # other paths...
]

