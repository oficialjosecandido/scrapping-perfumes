from rest_framework import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from rest_framework.test import APIRequestFactory
from ..models import *
from ..serializers import *
from .views import *
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest

import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
import re
from django.forms.models import model_to_dict
from rest_framework.response import Response

from .viewprices import *
from .viewbrand import extract_brands, extract_perfumes
from .viewdetails import *


# views for brands
def get_brands(request):
    response = extract_brands(request)
    return response


# views for brands
def get_notino(request):
    response = getNotino(request)
    return response

# views for fragrantica details
def getDetails(request):
    response = extract_one_details(request)
    return response

# views for fragrantica details
def getReviews(request):
    response = get_reviews(request)
    return response

def getPrices(request, id):
    print(id)
    getProductPrices(id)
    pass

# get similar perfumes
def getSimilares():
    pass
