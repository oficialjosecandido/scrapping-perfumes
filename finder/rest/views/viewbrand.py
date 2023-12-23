import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest
from rest.models import Brand
import re
from django.forms.models import model_to_dict
import html5lib
from rest_framework.response import Response
from datetime import datetime

baseUrl = 'https://www.fragrantica.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

brandsList = []
brands = Brand.objects.all()


def createBrandList():
    for brand in brands:
        brandsList.append(brand.fragrantica_url)

@api_view(['GET'])
def extract_brands(request):
    createBrandList()

    try:
        r = requests.get('https://www.fragrantica.com/designers', headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')
        
        designers = soup.find_all('div', class_="designerlist")

        for item in designers:
            for link in item.find_all('a', href=True):
                url = baseUrl + link['href']
                if url not in brandsList:
                    image_tag = item.find('img')
                    image_link = image_tag.get('src') if image_tag else None

                    brand_name_tag = item.find('a')
                    brand_name = brand_name_tag.text.strip() if brand_name_tag else None

                    url = url.replace('//designers', '/designers')
                    

                    # print('brand created....', brand_name, url, image_link)

                    print('appending new brand....', item)
                    Brand.objects.create(
                        fragrantica_url=url,
                        name = brand_name,
                        logo = baseUrl + image_link if image_link else None,
                        updated = datetime.now()
                    )
                    brandsList.append(url)
                else:
                    print('brand list is updated')

        return Response({'brands': brandsList})
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)})
    

def extract_perfumes(request):
    perfumeList = []
    url = 'https://www.fragrantica.com/designers/Ariana-Grande.html'
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')

        perfumes = soup.find_all('div', class_="px1-box-shadow")
        for item in perfumes:

            link = item.find('a', href=True)
            perfume_name_tag = item.find('a', href=True)
            perfume_name = perfume_name_tag.text.strip() if perfume_name_tag else None

            sku = baseUrl + link['href']
            sku = sku.replace('//perfume', '/perfume')

            print('perfume....', perfume_name, sku)
        
        return Response({'perfumes': perfumeList})
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)})