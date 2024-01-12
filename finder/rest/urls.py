from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views


urlpatterns = [
    
    path('brands', views.get_brands, name='brands'),
    path('notino', views.get_notino, name="sephora"),
    path('get_club', views.get_club, name='get_club')
    # path('get_reviews', views.getReviews, name='get_reviews'),

    # path('teste/', views.testAPI),
    # other paths...
]

