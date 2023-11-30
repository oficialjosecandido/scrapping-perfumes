import requests
from bs4 import BeautifulSoup

url = "https://www.sephora.fr/p/making-spirits-glam---coffret-maquillage-teint-et-yeux-P10052977.html"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

response = requests.get(url, headers=headers)
print("Response Status Code:", response.status_code)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract information based on the HTML structure of the page
    product_title = soup.find("h1", class_="product-title-heading").text.strip()
    product_price = soup.find("div", class_="product-price st-price").find("span", class_="price-sales").text.strip()

    # Print the extracted information
    print("Product Title:", product_title)
    print("Product Price:", product_price)
else:
    print("Failed to retrieve the webpage.")
