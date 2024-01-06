
from celery import shared_task
from django.conf import settings
from .views.viewbrand import *

@shared_task
def extract_brands_task():
    extract_brands()
