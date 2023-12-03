import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from rest.models import Perfume


@api_view(['GET'])
def getProductAccords(request):
    identifier = request.GET.get('identifier', None)
    product = Perfume.objects.get(identifier=identifier)
    if not identifier:
        return HttpResponseBadRequest("Brand and Model parameters are required.")

    url = product.fragrantica_url
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    # Send an HTTP request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main accords and their widths
        accords_data = [
            {
                'name': accord.text.strip(),
                'intensity': int(float(accord['style'].split('width: ')[1].split('%')[0]))
            }
            for accord in soup.select('.accord-bar')
        ]

        product.accords = accords_data
        product.save()

        # Print the list of main accords with widths
        print("Accords Data:", accords_data)

        # Return a JSON response with main accords and widths
        return JsonResponse({'accords_data': accords_data})
    else:
        print("Failed to retrieve the webpage.")


@api_view(['GET'])
def getFragranceNotes(request):
    identifier = request.GET.get('identifier', None)
    product = Perfume.objects.get(identifier=identifier)
    if not identifier:
        return HttpResponseBadRequest("Brand and Model parameters are required.")

    url = product.fragrantica_url
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    # Send an HTTP request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the description div
        description_div = soup.find('div', {'itemprop': 'description'})

        # Extract the text from the description div
        description_text = description_div.get_text() if description_div else ""

        # Extract notes from the description text
        top_notes = extract_notes("Top notes", description_text)
        middle_notes = extract_notes("Middle notes", description_text)
        base_notes = extract_notes("Base notes", description_text)

        # Update the perfume model with the extracted notes
        product.top_notes = top_notes
        product.middle_notes = middle_notes
        product.base_notes = base_notes
        product.save()

        # Return a JSON response with the extracted notes
        return JsonResponse({
            'top_notes': top_notes,
            'middle_notes': middle_notes,
            'base_notes': base_notes
        })
    else:
        print("Failed to retrieve the webpage.")

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

    # Send an HTTP request to the URL with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the description div
        description_div = soup.find('div', {'itemprop': 'description'})

        # Extract the text from the description div
        description_text = description_div.get_text() if description_div else ""

        # Search for olfactory family in the description text
        olfactory_family = search_olfactory_family(description_text)

        # Update the perfume model with the olfactory family
        product.olfactory_family = olfactory_family
        product.save()

        # Return a JSON response with the olfactory family
        return JsonResponse({'olfactory_family': olfactory_family})
    else:
        print("Failed to retrieve the webpage.")
        # Return an error JSON response
        return JsonResponse({'error': 'Failed to retrieve the webpage.'})
    
def search_olfactory_family(description_text):
    
    olfactory_classification = {
        "Amber Floral", "Amber Fougere", "Amber Spicy", "Amber Vanilla", "Amber Woody",
        "Aromatic Aquatic", "Aromatic Fougere", "Aromatic Fruity", "Aromatic Green", "Aromatic Spicy",
        "Chypre Floral", "Chypre Fruity",
        "Citrus Aromatic", "Citrus Gourmand",
        "Floral Aldehyde", "Floral Aquatic", "Floral Fruity", "Floral Fruity Gourmand", "Floral Green", "Floral Woody Musk",
        "Leather",
        "Woody Aquatic", "Woody Aromatic", "Woody Chypre", "Woody Floral Musk", "Woody Spicy"
    }


    # Search for olfactory family keywords in the description text
    for family in olfactory_classification:
        if family.lower() in description_text.lower():
            return family

    # Return None if no match is found
    return None

def extract_notes(section, text):
    # Search for the section header in both upper and lower case
    section_headers = [section, section.lower(), section.upper(), section.capitalize()]

    for header in section_headers:
        # Find the starting index of the section header
        start_index = text.find(header)
        if start_index != -1:
            # Find the ending index of the section
            end_index = text.find(";", start_index)  # You might need to adjust this based on your text structure

            # Extract the section text
            section_text = text[start_index:end_index].strip()

            # Remove unwanted words
            unwanted_words = ["Top notes", "Middle notes", "Base notes", "top notes", "middle notes", "base notes", "Notes", "notes", "are"]
            for word in unwanted_words:
                section_text = section_text.replace(word, "").strip()
            
            # Replace "and" with ","
            section_text = section_text.replace("and", ",")

            # Split the section text into a list of notes
            notes = [note.strip() for note in section_text.split("and")]

            # For base notes, consider only the text before the dot
            if section.lower() == "base notes":
                notes = [note.split(".")[0].strip() for note in notes]

            return notes

    # Return None if the section is not found
    return None


