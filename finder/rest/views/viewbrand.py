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
from selenium import webdriver


baseUrl = 'https://www.fragrantica.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

brandsList = []
brands = Brand.objects.all()


@api_view(['GET'])
def extract_brands(request):
    check_perfumes()
    # remove_duplicates()
    # remove_empty()
    # get_similar_and_nez()
    get_perfumes_brand(request)

    return Response({'brands': 'brandsList'})

def extract_one_details(request, sku):
    skuList = []
    print('extracting info from this URL...', sku)
    try:
        r = requests.get(sku, headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')

        # Create a Product
        product = Perfume.objects.create(
            fragrantica_url=sku,
            updated=datetime.now()
        )

        # Retrieve basic product info
        fragrance_info = extract_fragrance_info(soup.find('div', {'itemprop': 'description'}))
        product.model = fragrance_info['fragrance_name']
        product.brand = fragrance_info['fragrance_brand']
        product.year = fragrance_info['launch_year'] if fragrance_info['launch_year'] else ''

        # Get the nose
        les_nez = []
        designer_div = soup.find('div', class_="grid-x grid-padding-x grid-padding-y small-up-2 medium-up-2")
        if designer_div:
            for designer in designer_div.find_all('div', class_="cell"):
                designer_name = designer.find('a').get_text()
                les_nez.append(designer_name)
        product.le_nez = les_nez

        # Description and image
        product.description = fragrance_info['description']
        img_tag = soup.find('img', {'itemprop': 'image'})
        product.image = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

        # Olfactory family
        description_text = soup.find('div', {'itemprop': 'description'}).get_text() if soup.find('div', {'itemprop': 'description'}) else ""
        product.olfactory_family = search_olfactory_family(description_text)

        # Accords
        accords_data = [
            {
                'name': accord.text.strip(),
                'intensity': int(float(accord['style'].split('width: ')[1].split('%')[0]))
            }
            for accord in soup.select('.accord-bar')
        ]
        product.accords = accords_data

        # Olfactory notes
        top_notes = extract_notes("Top notes", description_text)
        middle_notes = extract_notes("Middle notes", description_text)
        base_notes = extract_notes("Base notes", description_text)
        product.top_notes = top_notes
        product.middle_notes = middle_notes
        product.base_notes = base_notes

        # Send a report if some notes are blank
        if (top_notes and len(top_notes) == 0) or (middle_notes and len(middle_notes) == 0) or (base_notes and len(base_notes) == 0):
            print('Finder | Produto com defeito na importação da pirâmide olfactiva')
            send_mail(
                'Finder | Produto com defeito na importação',
                'O {} tem defeitos na importação'.format(product.brand + " " + product.model),
                settings.EMAIL_HOST_USER,
                ['secretaria@tejomag.pt'],
                fail_silently=False
            )

        product.save()

        # Extract similar and nez details
        similar_urls = []
        similar_div = soup.find('div', class_="strike-title", string="People who like this also like")
        if similar_div:
            carousel = similar_div.find_next('div', class_="carousel")
            perfume_cells = carousel.find_all('div', class_="carousel-cell")

            for cell in perfume_cells:
                perfume_url = cell.find('a')['href']
                full_url = f'https://www.fragrantica.com{perfume_url}'
                similar_urls.append(full_url)

            print(product.model)
            product.similar = similar_urls
            product.save()
            # time.sleep(240)  # 600 seconds = 10mins

        if sku not in skuList:
            perfume_name = product.model
            message = f'Perfume "{perfume_name}" was created.'
            print(message)
            product.creation_message = message

        return render(request, 'rest/perfumes.html', {'perfume_details': model_to_dict(product)})

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
    for family in olfactory_classification:
        if family in description_text:
            return family
    return None

def get_perfumes_brand(request):

    for designer in Brand.objects.all():
        try:
            r = requests.get(designer.fragrantica_url, headers=headers)
            r.raise_for_status() 
            soup = BeautifulSoup(r.content, 'html.parser')

            brand_perfumes = Perfume.objects.filter(brand=designer.name)
            sku_list = [perfume.fragrantica_url for perfume in brand_perfumes]

            perfumeDIV = soup.find_all('div', class_="px1-box-shadow")
            for item in perfumeDIV:

                link = item.find('a', href=True)
                perfume_name_tag = item.find('a', href=True)
                perfume_name = perfume_name_tag.text.strip() if perfume_name_tag else None

                sku = baseUrl + link['href']
                sku = sku.replace('//perfume', '/perfume')

                if any(sku == s for s in sku_list):
                    print(f"{perfume_name} already extracted.")
                else:
                    extract_one_details(request, sku)
                    time.sleep(240)  # 600 seconds = 10mins
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)})
        

def remove_duplicates():
    
    duplicate_names = Perfume.objects.values('model').annotate(name_count=Count('model')).filter(name_count__gt=1)

    # Iterate over duplicate names
    for duplicate in duplicate_names:
        name = duplicate['model']
        
        # Get all Perfume objects with the duplicate name
        duplicate_perfumes = Perfume.objects.filter(model=name)
        
        # Keep one instance and delete the rest
        first_perfume = duplicate_perfumes.first()
        duplicate_perfumes.exclude(pk=first_perfume.pk).delete()


def remove_empty():
    for perfume in Perfume.objects.all():
        if perfume.model == '':
            perfume.delete()

def check_perfumes():
    try:
        r = requests.get('https://www.fragrantica.com/designers', headers=headers)
        r.raise_for_status() 
        soup = BeautifulSoup(r.content, 'html.parser')
        
        designers = soup.find_all('div', class_="designerlist")

        brandList = []

        for brand in Brand.objects.all():
            brandList.append(brand.fragrantica_url)

        for item in designers:
            for link in item.find_all('a', href=True):
                url = baseUrl + link['href']
                url = url.replace('//designers', '/designers')
                brand_name_tag = item.find('a')
                perfumes = item.find('span', class_="badge").get_text()
                brand_name = brand_name_tag.text.strip() if brand_name_tag else None
                    
                # update the brands list
                if url not in brandList:
                    image_tag = item.find('img')
                    image_link = image_tag.get('src') if image_tag else None
                    
                    print('appending new brand....', item)
                    Brand.objects.create(
                        fragrantica_url=url,
                        name = brand_name,
                        perfumes = perfumes,
                        logo = baseUrl + image_link if image_link else None,
                        updated=timezone.now()
                    )
                    brandsList.append(url)
                else:
                    brand = Brand.objects.get(fragrantica_url=url, name=brand_name)
                    # check if the brand has new perfumes
                    if brand.perfumes != perfumes:
                        print('new perfumes have been inserted into...', brand_name)
                    else:
                        brand.perfumes = perfumes
                        brand.save()
                    print(brand_name, 'is updated successfully')

        
        return Response({'brands': brandsList})
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)})

def get_similar_and_nez():
    for perfume in Perfume.objects.all().iterator(chunk_size=620):
        print(perfume.model)
        if perfume.similar == '':
            try:
                r = requests.get(perfume.fragrantica_url, headers=headers)
                r.raise_for_status() 
                soup = BeautifulSoup(r.content, 'html.parser')

                les_nez = []

                # Find the div containing perfumer information
                perfumer_div = soup.select_one('div.cell.small-12')

                if perfumer_div:
                    # Find all perfumer names within the div
                    perfumer_elements = perfumer_div.select('div.cell > a')

                    for perfumer_element in perfumer_elements:
                        perfumer_name = perfumer_element.text.strip()
                        les_nez.append(perfumer_name)

                    print(les_nez)
                    perfume.le_nez = les_nez
                    perfume.save()

                # Move similar_urls inside the loop to reset it for each perfume
                similar_urls = []

                # Find the div containing similar perfumes
                similar_div = soup.find('div', class_="strike-title", string="People who like this also like")

                if similar_div:
                    # Extract perfume URLs from the carousel
                    carousel = similar_div.find_next('div', class_="carousel")
                    perfume_cells = carousel.find_all('div', class_="carousel-cell")

                    for cell in perfume_cells:
                        perfume_url = cell.find('a')['href']
                        full_url = f'https://www.fragrantica.com{perfume_url}'
                        
                        similar_urls.append(full_url)

                    print(perfume.model)
                    perfume.similar = similar_urls
                    perfume.save()
                    time.sleep(240)  # 600 seconds = 10mins

            except Exception as e:
                print('Failed:', str(e))
                return None
        else:
            print('Perfume notes already updated')

    return Response({'perfumes': Perfume.objects.all()})