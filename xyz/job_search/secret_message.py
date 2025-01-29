from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def get_docs_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_608925455483-6j8mj8jh1t0kaqmsdf6oi79hb52f2opm.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('docs', 'v1', credentials=creds)

service = get_docs_service()

DOCUMENT_ID = '2PACX-1vRMx5YQlZNa3ra8dYYxmv-QIQ3YJe8tbI3kqcuC7lQiZm-CSEznKfN_HYNSpoXcZIV3Y_O3YoUB1ecq'

document = service.documents().get(documentId=DOCUMENT_ID).execute()
content = document.get('body').get('content')


def extract_tables(content):
    tables = []
    current_table = None
    current_row = None

    for element in content:
        if 'table' in element:
            current_table = []
            tables.append(current_table)
        elif 'tableRow' in element:
            current_row = []
            current_table.append(current_row)
        elif 'tableCell' in element:
            cell_content = element['tableCell']['content']
            cell_text = ''
            for item in cell_content:
                if 'paragraph' in item:
                    for run in item['paragraph']['elements']:
                        if 'textRun' in run:
                            cell_text += run['textRun']['content']
            current_row.append(cell_text.strip())

    return tables

tables = extract_tables(content)

for i, table in enumerate(tables):
    print(f"Table {i + 1}:")
    df = pd.DataFrame(table[1:], columns=table[0])  # Assuming the first row is headers
    print(df)
    print("\n")
