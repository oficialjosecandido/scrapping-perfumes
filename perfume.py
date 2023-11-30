import requests
from bs4 import BeautifulSoup

url = "https://www.perfumesclub.fr/fr/lancome/la-vie-est-belle-eau-de-parfum-vaporisateur/p_35520/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

response = requests.get(url, headers=headers)
#print("Response Status Code:", response.status_code)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract information based on the HTML structure of the page
    product_brand = soup.find("h1", class_="titleProduct").find("a").text.strip()
    product_model = soup.find("h1", class_="titleProduct").find("span").text.strip()
    #product_price = soup.find("div", class_="product-price st-price").find("span", class_="price-sales").text.strip()

    # Print the extracted information
    print("Product Model:", product_model)
    print("Product Brand:", product_brand)
    #print("Product Price:", product_price)
    
else:
    print("Failed to retrieve the webpage.")
