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
from rest_framework.response import Response
from selenium import webdriver



baseUrl = 'https://www.notino.fr'
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


perfume = 'Chanel Antaeus'

def getProductPrices(id):
    pass

@api_view(['GET'])
def getNotino(request):
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


    perfumeName = 'Guilty Absolute'
    perfume_url = perfumeName.replace(' ', '%20')
    url = baseUrl + '/search.asp?exps=' + perfume_url
    print('url da pesquisa....', url)

    # Use Selenium to load the page and wait for dynamic content
    driver = webdriver.Chrome()  # You might need to adjust the path to your chromedriver
    driver.get(url)
    
    # Wait for the dynamic content to load, you might need to adjust the wait time
    driver.implicitly_wait(10)

    # Get the page source after JavaScript execution
    page_source = driver.page_source

    # Use BeautifulSoup to parse the loaded content
    soup = BeautifulSoup(page_source, 'html.parser')

    # Locate perfume divs using data-testid attribute
    perfumes = soup.find_all('div', {'data-testid': 'product-container'})

    product_names = []
    for perfume in perfumes:
    # Extract the product name
        product_name_element = perfume.find('h3', class_="sc-eqUAAy sc-krNlru dbGhzH dbyWUd")
        if product_name_element:
            product_name = product_name_element.get_text()
            print("Product Name:", product_name)
            if product_name == perfumeName:
                links = perfume.find_all('a', href=True)
                for link in links:
                    print('Ok that is a match!!!!', link['href'])
        product_names.append(product_name)

    driver.quit()  # Close the Selenium WebDriver

    # Return a JSON response with the product names
    return Response({'names': product_names})

    """ try:
        r = requests.get(url, headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')
        
        designers = soup.find_all('div', class_="designerlist")

        return Response({'prices': 'brandsList'})
    
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}) """