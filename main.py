# main.py
import json
import requests
import lxml
from bs4 import BeautifulSoup

# Constants
URL = 'https://market.csgo.com/?r=&q=&p=1&h='
HEADERS = {

    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'

} 

# Ask user for starting page and the number of pages to parse
input_pages_count = int(input('How many pages do you wish to parse? --> '))
input_starting_page = int(input('Which page do you want to start from? --> '))

"""
Function to get data

Arguments: 
    1. page - First page to start the iteration from
    2. pages_count - How many pages to iterate through (Write '1' to only get the page you choosed)
"""
def get_data(page=0, pages_count=1):
    i = 0

    while i != pages_count:
        if page == 0:    
            page += 1

        print(f'Parsing the page -- {page}')

        url = f'https://market.csgo.com/?r=&q=&p={page}&h='

        # Request the html code of the page
        req = requests.get(url=url, headers=HEADERS)
        src = req.text 
        
        # 'Cook' the soup 
        soup = BeautifulSoup(src, 'lxml')

        # Create the list and dictionary of products
        products = soup.find('div', class_='market-items', id='applications').find_all('a')
        products_dict = {}

        # Iterate through every product and write it in a dictionary we just created
        for product in products:
            product_name = product.find('div', class_='name').text.strip()
            product_link = 'https://market.csgo.com' + product.get('href').strip()

            products_dict[product_name] = product_link
        
        i += 1
        page += 1

    # Dump the dictionary into 'json' file
    with open('products_dict.json', 'w', encoding='utf-8') as file:
        json.dump(products_dict, file, indent=4, ensure_ascii=False)

    print('Done! All the products and the links to them are stored in the JSON file named "products_dict.json"')

get_data(pages_count=input_pages_count, page=input_starting_page)

with open("products_dict.json", encoding='utf-8') as file:
    all_products = json.load(file)

iteration_count = int(len(all_products)) - 1
count = 0

print(f"Iterations count: {iteration_count}")

final_products_dict = {}
i = 0

# A loop where we get the info about every product available
for product_name, product_link in all_products.items():
    rep = [',', ' ', '-', '\'', '|', '/', '\\']
    for char in rep:
        if char in product_name:
            product_name = product_name.replace(char, '_')

    req = requests.get(url=product_link, headers=HEADERS)
    src = req.text

    with open(f"data/{count}_{product_name}.html", "w", encoding='utf-8') as file:
        file.write(src)

    with open(f"data/{count}_{product_name}.html", encoding='utf-8') as file:
        src = file.read()
        
    print(f"Looking for --> {product_name}")

    soup = BeautifulSoup(src, "lxml")

    product_name = soup.find('h1').text
        
    # Skip the Advertisement
    if product_name == 'Тренировки по киберспорту':
        continue
    else:
        try:    
            product_cost = soup.find('div', class_='ip-bestprice').text.strip() + " RUB"

            product_min_cost = soup.find_all('div', class_='rectanglestat')[1].find('b').text.strip() + " RUB"
                
            product_max_cost = soup.find_all('div', class_='rectanglestat')[2].find('b').text.strip() + " RUB"

            product_avg_cost = soup.find_all('div', class_='rectanglestat')[3].find('b').text.strip() + " RUB"
        except Exception as e:
            product_cost = 'Unavailable'
        
    final_products_dict[product_name] = {

        'Cost': product_cost,
        'Minimum Cost': product_min_cost,
        'Maximum Cost': product_max_cost,
        'Average Cost': product_avg_cost

    }
        
with open('information.json', 'w', encoding='utf-8') as file:
    json.dump(final_products_dict, file, indent=4, ensure_ascii=False)