import requests
from bs4 import BeautifulSoup


def read_published_google_doc(url):
    """
    :param url: The URL of the published Google Doc to be read.
    :return: A list of tuples where each tuple contains three elements (x, char, y) extracted from the table rows.
             Returns None if the request fails.
    """
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all table rows (tr elements)
        rows = soup.find_all('tr')

        # Extract and print the data
        data = []
        for row in rows[1:]:  # Skip the header row
            cols = row.find_all('td')
            if len(cols) == 3:
                x = cols[0].text.strip()
                char = cols[1].text.strip()
                y = cols[2].text.strip()
                data.append((x, char, y))

        return data
    else:
        print(f"Failed to retrieve the document. Status code: {response.status_code}")
        return None


def process_table_data(data):
    """
    :param data: A list of tuples, where each tuple contains three elements.
                 The first element is the x-coordinate (as a string that can be converted to an integer),
                 the second element is a character to be placed in the grid,
                 and the third element is the y-coordinate (as a string that can be converted to an integer).
    :return: None
    """
    # Find the dimensions of the grid
    max_x = max(int(row[0]) for row in data)
    max_y = max(int(row[2]) for row in data)

    # Create an empty grid filled with spaces
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    # Fill the grid with characters
    for x, char, y in data:
        grid[int(y)][int(x)] = char

    # Print the grid
    for row in grid:
        print(''.join(row))


# URL of the published Google Doc
url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"

# Read the data
table_data = read_published_google_doc(url)

process_table_data(table_data)
