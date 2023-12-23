import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseBadRequest
from rest.models import Perfume
import re
from django.forms.models import model_to_dict
import html5lib

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

    for family in olfactory_classification:
        if family.lower() in description_text.lower():
            return family

    return None

def extract_fragrance_info(text):
    soup = BeautifulSoup(text, 'html.parser')
    description_div = soup.find('div', {'itemprop': 'description'})
    description_text = description_div.get_text() if description_div else ""
    bold_elements = description_div.find_all('b')

    fragrance_name = bold_elements[0].get_text().strip() if bold_elements else None
    fragrance_brand = bold_elements[1].get_text().strip() if len(bold_elements) > 1 else None

    launch_year = None
    launch_year_pattern = re.compile(r'\b\d{4}\b')
    match = launch_year_pattern.search(description_text)
    if match:
        launch_year = match.group()

    return {
        'fragrance_name': fragrance_name,
        'fragrance_brand': fragrance_brand,
        'launch_year': launch_year
    }

def get_webpage_data(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        return None

def parse_html_for_accords(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    accords_data = [
        {
            'name': accord.text.strip(),
            'intensity': int(float(accord['style'].split('width: ')[1].split('%')[0]))
        }
        for accord in soup.select('.accord-bar')
    ]

    return accords_data

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
    parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("beautifulsoup"))
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


def parse_html_for_notes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    description_div = soup.find('div', {'itemprop': 'description'})
    description_text = description_div.get_text() if description_div else ""

    top_notes = extract_notes("Top notes", description_text)
    middle_notes = extract_notes("Middle notes", description_text)
    base_notes = extract_notes("Base notes", description_text)

    return {
        'top_notes': top_notes,
        'middle_notes': middle_notes,
        'base_notes': base_notes
    }

@api_view(['GET'])
def getProductAccords(request):
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
        accords_data = parse_html_for_accords(html_content)
        product.accords = accords_data
        product.save()
        print("Accords Data:", accords_data)
        return JsonResponse({'accords_data': accords_data})
    else:
        print("Failed to retrieve the webpage.")
        return JsonResponse({'error': 'Failed to retrieve the webpage.'})


@api_view(['GET'])
def getFragranceNotes(request):
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
        notes_data = parse_html_for_notes(html_content)
        product.top_notes = notes_data['top_notes']
        product.middle_notes = notes_data['middle_notes']
        product.base_notes = notes_data['base_notes']
        product.save()
        return JsonResponse(notes_data)
    else:
        print("Failed to retrieve the webpage.")
        return JsonResponse({'error': 'Failed to retrieve the webpage.'})

@api_view(['GET'])
def getFragranceInfo(request):
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
        fragrance_info = extract_fragrance_info(html_content)
        product.fragrance_name = fragrance_info['fragrance_name']
        product.fragrance_brand = fragrance_info['fragrance_brand']
        product.launch_year = fragrance_info['launch_year']
        product.save()
        return JsonResponse(fragrance_info)
    else:
        print("Failed to retrieve the webpage.")
        # Convert Product object to a dictionary
        product_dict = model_to_dict(product)
        return JsonResponse({'error': product_dict})

@api_view(['GET'])
def getOlfactoryFamily(request):
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
        soup = BeautifulSoup(html_content, 'html.parser')
        description_div = soup.find('div', {'itemprop': 'description'})
        description_text = description_div.get_text() if description_div else ""
        olfactory_family = search_olfactory_family(description_text)
        product.olfactory_family = olfactory_family
        product.save()
        return JsonResponse({'olfactory_family': olfactory_family})
    else:
        print("Failed to retrieve the webpage.")
        return JsonResponse({'error': product})
