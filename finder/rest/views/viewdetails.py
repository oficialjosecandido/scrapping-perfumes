import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest
from rest.models import *
import re
from django.forms.models import model_to_dict
import html5lib
from rest_framework.response import Response
from datetime import datetime
import time

baseUrl = 'https://www.fragrantica.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


@api_view(['GET'])
def extract_one_details(request):
    sku = 'https://www.fragrantica.com/perfume/Chanel/Antaeus-616.html'
    product = Perfume.objects.get(fragrantica_url=sku)
    print(product)
    try:
        r = requests.get(sku, headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')


        # retrieve basic product info
        description_div = soup.find('div', {'itemprop': 'description'})
        fragrance_info = extract_fragrance_info(description_div)
        product.model = fragrance_info['fragrance_name']
        product.brand = fragrance_info['fragrance_brand']
        product.year = fragrance_info['launch_year']
        product.description = fragrance_info['description']
        img_tag = soup.find('img', {'itemprop': 'image'})
        product.image = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
        product.save()

        # retrieve olfactory family
        description_div = soup.find('div', {'itemprop': 'description'})
        description_text = description_div.get_text() if description_div else ""
        olfactory_family = search_olfactory_family(description_text)
        product.olfactory_family = olfactory_family
        product.save()

        # retrieve the accords
        accords_data = [
            {
                'name': accord.text.strip(),
                'intensity': int(float(accord['style'].split('width: ')[1].split('%')[0]))
            }
            for accord in soup.select('.accord-bar')
        ]
        product.accords = accords_data
        product.save()

        # get the olfactory notes
        description_div = soup.find('div', {'itemprop': 'description'})
        description_text = description_div.get_text() if description_div else ""
        top_notes = extract_notes("Top notes", description_text)
        middle_notes = extract_notes("Middle notes", description_text)
        base_notes = extract_notes("Base notes", description_text)
        product.top_notes = top_notes
        product.middle_notes = middle_notes
        product.base_notes = base_notes
        product.save()

        # Convert the Perfume object to a dictionary
        perfume_dict = model_to_dict(product)

        return Response({'perfume inserted': perfume_dict})
        
    
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)})
    


def extract_notes(section, text):
    section_headers = [section, section.lower(), section.upper(), section.capitalize()]

    for header in section_headers:
        start_index = text.find(header)
        if start_index != -1:
            end_index = text.find(";", start_index)
            section_text = text[start_index:end_index].strip()

            unwanted_words = ["Top notes", "Middle notes", "Base notes", "top notes", "middle notes", "base notes", "Notes", "notes", "are"]
            for word in unwanted_words:
                section_text = section_text.replace(word, "").strip()

            section_text = section_text.replace("and", ",")

            notes = [note.strip() for note in section_text.split("and")]

            if section.lower() == "base notes":
                notes = [note.split(".")[0].strip() for note in notes]

            return notes

    return None


def extract_fragrance_info(description_div):
    
    description_text = description_div.get_text() if description_div else ""
    bold_elements = description_div.find_all('b')

    fragrance_name = bold_elements[0].get_text().strip() if bold_elements else None
    fragrance_brand = bold_elements[1].get_text().strip() if len(bold_elements) > 1 else None

    launch_year = None
    launch_year_pattern = re.compile(r'\b\d{4}\b')
    match = launch_year_pattern.search(description_text)
    if match:
        launch_year = match.group()

    # Cut everything after "Read about this perfume in other languages:"
    description_split = description_text.split("Read about this perfume in other languages:")
    description = description_split[0].strip() if description_split else None

    

    return {
        'fragrance_name': fragrance_name,
        'fragrance_brand': fragrance_brand,
        'launch_year': launch_year,
        'description': description,
    }


def search_olfactory_family(description_text):
    olfactory_classification = {
        "Amber", "Amber Floral", "Amber Fougere", "Amber Spicy", "Amber Vanilla", "Amber Woody",
        "Aromatic Aquatic", "Aromatic Fougere", "Aromatic Fruity", "Aromatic Green", "Aromatic Spicy",
        "Chypre Floral", "Chypre Fruity",
        "Citrus Aromatic", "Citrus Gourmand",
        "Floral Aldehyde", "Floral Aquatic", "Floral Fruity", "Floral Fruity Gourmand", "Floral Green", "Floral Woody Musk",
        "Leather",
        "Woody Aquatic", "Woody Aromatic", "Woody Chypre", "Woody Floral Musk", "Woody Spicy"
    }
    print(description_text)
    for family in olfactory_classification:
        if family in description_text:
            return family
    return None


