import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep


def get_data(search_query, pages=4, sleep_time=1.5):
    """
    Retrieve product data from Amazon based on a search query.
    Desired data to be retrieved are : product name,  rating , rating count , price and product URL

    :param search_query: A string representing the search query.
    :param pages: An integer representing the number of search result pages to process (default: 4).
    :param sleep_time: A float representing the sleep time in seconds between processing pages (default: 1.5).
    :return: A list of lists containing the product information.
    """
    # Define headers for the HTTP request to Amazon
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    # Format search query for use in a URL by replacing spaces with '+'
    search_query = search_query.replace(' ', '+')

    # Construct the base URL for the Amazon search page using the formatted search query
    base_url = 'https://www.amazon.com/s?k={0}'.format(search_query)

    # Create an empty list to store the scraped items
    items = []

    # Loop through the specified number of search result pages
    for i in range(1, pages + 1):
        # Print the current URL being processed
        print('Processing {0}...'.format(base_url + '&page={0}'.format(i)))

        # Send an HTTP GET request to the current search result page URL
        response = requests.get(base_url + '&page={0}'.format(i), headers=headers)

        # Parse the HTML content of the response using Beautiful Soup
        soup = BeautifulSoup(response.content, 'lxml')

        # Find all product result items on the page using the specified class and data-component-type attributes
        results = soup.find_all('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})

        # Iterate through each product result item
        for result in results:
            # Extract the product name from the h2 tag
            product_name = result.h2.text

            # Try to extract the rating and rating count, skip the current iteration if not found
            try:
                rating = result.find('i', {'class': 'a-icon'}).text
                rating_count = result.find_all('span', {'aria-label': True})[1].text
            except AttributeError:
                continue

            # Try to extract the price and product URL, skip the current iteration if not found
            try:
                price1 = result.find('span', {'class': 'a-price-whole'}).text
                price2 = result.find('span', {'class': 'a-price-fraction'}).text
                price = price1 + price2
                product_url = 'https://amazon.com' + result.h2.a['href']
                items.append([product_name, rating, rating_count, price, product_url])
            except AttributeError:
                continue

        # Sleep for the specified time to avoid overwhelming the server with requests
        sleep(sleep_time)

    return items


def converting_to_csv(items, search_query):

    """
    Convert the list of product information to a CSV file.

    :param items: A list of lists containing the product information.
    :param search_query: A string representing the search query, used as the CSV file name
"""
    # Create a pandas DataFrame using the list of items and specify the column names
    df = pd.DataFrame(items, columns=['product', 'rating', 'rating count', 'price', 'product url'])

    # Save the DataFrame to a CSV file using the search query as the file name, without including the index
    df.to_csv('{0}.csv'.format(search_query), index=False)


def main():
    # Prompt the user to enter their search query
    search_query = input("Enter your search query: ")

    # Retrieve the product information based on the user's search query
    items = get_data(search_query, pages=1)

    # Save the product information to a CSV file
    converting_to_csv(items, search_query)


if __name__ == '__main__':
    main()
