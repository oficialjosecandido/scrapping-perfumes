import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest
from rest.models import *
import re
from django.forms.models import model_to_dict
from rest_framework.response import Response
from datetime import datetime
import time
from django.utils import timezone
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count

baseUrl = 'https://www.fragrantica.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
clubList = []

@api_view(['GET'])
def get_perfumes_club(request):

    try:
        r = requests.get('https://www.perfumesclub.com/es/acqua-di-parma/m/', headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')

        perfumeList = soup.find_all('div', class_="productList gamas pagina1 col-6 col-md-4 col-lg-4 col-xl-4 newLayOut GTMImpressionClick")
        

        for item in perfumeList:
            for link in item.find_all('a', href=True):
                url = baseUrl + link['href']
                if not url.endswith('/m/'):
                    clubList.append(url)
                    print(url)
        
        print(len(clubList))

        match_perfumes() 


        return Response({'brands': 'brandsList'})
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)})
    


def match_perfumes():

    club_slug = []
    perfumes_slug = []


    # for perfume in Perfume.objects.all():


    for item in clubList:
        # Find the index of "es/"
        es_index = item.find("/acqua-di-parma/") + len("/acqua-di-parma/")
        
        # Find the index of "/p_"
        p_index = item.find("/p_", es_index)
        
        # Extract the substring between "es/" and "/p_"
        perfume_info = item[es_index:p_index]
        club_slug.append(perfume_info)
        
    print(club_slug)
        