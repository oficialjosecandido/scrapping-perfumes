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
import html5lib
from rest_framework.response import Response

from .viewprices import getProductPrices
from .viewaccords import getProductAccords, getOlfactoryFamily, getFragranceNotes, getFragranceInfo
from .viewbrand import extract_brands, extract_perfumes

baseUrl = 'https://www.fragrantica.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# views for brands
def get_brands(request):
    response = extract_perfumes(request)
    return response


def getPrices(request, id):
    print(id)
    getProductPrices(id)
    pass


@api_view(['GET'])
def get_data(request):
    identifier = request.GET.get('identifier', None)
    
    # Check if identifier is provided
    if not identifier:
        return HttpResponseBadRequest("Brand and Model parameters are required.")
    
    # Create APIRequestFactory instance
    factory = APIRequestFactory()

    # Create Request instances for individual views
    info_request = factory.get('/getFragranceInfo', {'identifier': identifier})
    accords_request = factory.get('/getProductAccords', {'identifier': identifier})
    notes_request = factory.get('/getFragranceNotes', {'identifier': identifier})
    # product_reactions_request = factory.get('/getProductReactions', {'identifier': identifier})
    olfactory_request = factory.get('/getOlfactoryFamily', {'identifier': identifier})

    # Call the individual views
    info_response = getFragranceInfo(info_request)
    accords_response = getProductAccords(accords_request)
    notes_response = getFragranceNotes(notes_request)
    # product_reactions_response = getProductReactions(product_reactions_request)
    olfactory_response = getOlfactoryFamily(olfactory_request)
    
    # Combine the responses into a single JSON response
    combined_response = {
        'fragrance_info': info_response.data,
        'product_accords': accords_response.data,
        'fragrance_notes': notes_response.data,
        'olfactory_family': olfactory_response.data,
        # "product reactions": product_reactions_response.data
    }

    return JsonResponse(combined_response)


def getReactions(request):
    response = getProductReactions(request)
    return response

def getInfo(request):
    response = getFragranceInfo(request)
    return response

def getAccords(request):
    response = getProductAccords(request)
    return response

def getNotes(request):
    response = getFragranceNotes(request)
    return response

def getOlfactory(request):
    response = getOlfactoryFamily(request)
    return response


def get_webpage_data(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        return None



@api_view(['GET'])
def getProductReactions(request):
    identifier = request.GET.get('identifier', None)
    product = Perfume.objects.get(identifier=identifier)

    if not identifier:
        return HttpResponseBadRequest("Brand and Model parameters are required.")

    url = product.fragrantica_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    html_content = get_webpage_data(url, headers)
    if html_content:
        model_attributes_data = parse_html_for_model_attributes(html_content)
        product.model_attributes = model_attributes_data
        product.save()
        print("Model Attributes Data:", model_attributes_data)
        return JsonResponse({'model_attributes_data': model_attributes_data})
    else:
        print("Failed to retrieve the webpage.")
        return JsonResponse({'error': 'Failed to retrieve the webpage.'})

def get_webpage_data(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        return None
    

def parse_html_for_model_attributes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Extracting model attributes data
    model_attributes_data = {
        'love': 0,
        'like': 0,
        'ok': 0,
        'dislike': 0,
        'hate': 0,
    }

    # Convert JavaScript logic to Python
    # Your HTML string (I'm using a placeholder, replace it with the actual HTML content)
    html_string = """<div class="grid-x grid-margin-x grid-margin-y">...</div>"""

    # Parse the HTML string into a DOM object
    doc = BeautifulSoup(html_string, 'html.parser')

    # Select all div elements with the specified style attribute
    div_elements = doc.select('div[style*="width"]')

    # Update values based on width property
    for div_element in div_elements:
        # Extract the width value from the style attribute
        width_match = re.search(r'width:\s*(\d+(\.\d+)?)%', div_element['style'])

        if width_match:
            width_value = float(width_match.group(1))

            # Update the corresponding property in the model_attributes_data object
            if 0 <= width_value <= 20:
                model_attributes_data['hate'] += 1
            elif 20 < width_value <= 40:
                model_attributes_data['dislike'] += 1
            elif 40 < width_value <= 60:
                model_attributes_data['ok'] += 1
            elif 60 < width_value <= 80:
                model_attributes_data['like'] += 1
            elif 80 < width_value <= 100:
                model_attributes_data['love'] += 1

    return model_attributes_data
