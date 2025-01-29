import os
from pathlib import Path
import docx
from PyPDF2 import PdfReader
import markdown
from bs4 import BeautifulSoup
import tiktoken

def num_tokens(text):
    """
    Counts the number of tokens in the given text using the tiktoken library.
    """
    try:
        # Get the encoding for the model
        encoding = tiktoken.encoding_for_model('gpt-4')
        # Encode the text to count tokens
        encoded_text = encoding.encode(text, disallowed_special=())
        token_count = len(encoded_text)
        return token_count
    except Exception as e:
        print(f"Error in num_tokens: {e}")
        return None

def read_word_document(file_path):
    """Reads the text content of a Word document."""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_pdf_document(file_path):
    """Reads the text content of a PDF document."""
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        full_text = []
        for page in pdf_reader.pages:
            full_text.append(page.extract_text())
    return '\n'.join(full_text)

def read_markdown_file(file_path):
    """Reads and converts a Markdown file to plain text."""
    with open(file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()
    html_content = markdown.markdown(md_content)
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def read_html_file(file_path):
    """Reads an HTML file and extracts its text content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def count_tokens_in_documents(directory):
    """
    Counts the tokens for each document in the specified directory.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory does not exist: {os.path.abspath(directory)}")

    print(f"Scanning directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('~$'):  # Skip temporary files
                continue

            if file.endswith(('.doc', '.docx', '.pdf', '.md', '.html')):
                file_path = os.path.join(root, file)

                try:
                    # Read the file based on its type
                    if file.endswith(('.doc', '.docx')):
                        raw_text = read_word_document(file_path)
                    elif file.endswith('.pdf'):
                        raw_text = read_pdf_document(file_path)
                    elif file.endswith('.md'):
                        raw_text = read_markdown_file(file_path)
                    elif file.endswith('.html'):
                        raw_text = read_html_file(file_path)
                    else:
                        print(f"Unsupported file type: {file}")
                        continue

                    # Count tokens in the text
                    token_count = num_tokens(raw_text)
                    if token_count is not None:
                        print(f"File: {file_path}")
                        print(f"Token Count: {token_count}\n")
                    else:
                        print(f"Failed to count tokens for file: {file_path}\n")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}\n")

# Specify the directory containing the documents
directory = "xyz/llm/knowledge_sources/personal"

# Run the script
count_tokens_in_documents(directory)
