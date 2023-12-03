from rest_framework import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from ..models import *
from ..serializers import *
from .views import *


from .viewprices import getProductPrices
from .viewaccords import getProductAccords, getOlfactoryFamily, getFragranceNotes

""" def newsAPI(request, id=0):
    news = News.objects.order_by('-date')[:4]
    news_serializer = FlashNewsSerializer(news, many=True)
    return JsonResponse(news_serializer.data, safe=False)  """

def getPrices(request, id):
    print(id)
    getProductPrices(id)
    pass

def getAccords(request):
    response = getProductAccords(request)
    return response

def getNotes(request):
    response = getFragranceNotes(request)
    return response

def getOlfactory(request):
    response = getOlfactoryFamily(request)
    return response

