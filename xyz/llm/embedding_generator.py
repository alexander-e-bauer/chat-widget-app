import os
from pathlib import Path
import docx
from PyPDF2 import PdfReader
import re
import pandas as pd
from scipy import spatial
import ast
import tiktoken
import tiktoken
import openai
import config
import xyz.llm.embedding_model as flask_embeddings
from xyz.llm.embedding_model import embedding_model, read_embedding, ask



log = config.log
OAI = config.OAI




def num_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o')
    encoding = encoding.encode(text, disallowed_special=())
    print(len(encoding))
    return len(encoding)


def save_text_to_file(text, file_path):
    file_path = Path(file_path)
    with open(file_path, 'w') as file:
        file.write(text)



def remove_stuff(text: str) -> str:
    """Remove punctuation (except in URLs), newline, tab characters, and large spaces."""
    # Pattern to identify URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # Find all URLs using the pattern
    urls = re.findall(url_pattern, text)
    # Replace URLs with a placeholder to avoid altering them
    placeholder = "URL_PLACEHOLDER"
    for url in urls:
        text = text.replace(url, placeholder)

    # Remove large spaces (5 or more spaces)
    text = re.sub(r' {5,}', ' ', text)

    # Restore URLs from placeholders
    for url in urls:
        text = text.replace(placeholder, url, 1)

    return text



def get_embedding(text_to_embed):
    text_to_embed = remove_stuff(text_to_embed)
    # Embed a line of text
    response = OAI.client.embeddings.create(
        model=embedding_model,
        input=[text_to_embed]
    )
    # Extract the AI output embedding as a list of floats
    embedding = response.data[0].embedding
    print(f"---\nEmbedding: {embedding} \nText: {text_to_embed}")

    return embedding


def get_source_code(directory):
    """Returns the source code of all Python files in a directory."""
    df = pd.DataFrame(columns=['filepath', 'text'])
    string = []
    paths = []
    for root, dirs, files in os.walk(directory):
        if root.startswith('./lib'):
            continue
        elif root.startswith('./bin'):
            continue
        elif root.startswith('./include'):
            continue
        else:
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    raw_text = read_file_as_raw_text(file_path)
                elif file.endswith(".html"):
                    file_path = os.path.join(root, file)
                    raw_text = read_file_as_raw_text(file_path)
                elif file.endswith(".css"):
                    file_path = os.path.join(root, file)
                    raw_text = read_file_as_raw_text(file_path)
                elif file.endswith(".js"):
                    file_path = os.path.join(root, file)
                    raw_text = read_file_as_raw_text(file_path)

                else:
                    continue
                log(f"Source code: {file_path}")
                string.append(raw_text), paths.append(file_path)

                df = df._append({'filepath': file_path, 'text': raw_text}, ignore_index=True)

    return df




def get_document_text(directory):
    """
    Returns the text content and embeddings of all Word documents and PDFs in a directory,
    or from an Excel file if provided.
    """
    df = pd.DataFrame(columns=['filepath', 'text', 'embedding'])

    # Process documents in directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('~$'):
                continue

            if file.endswith(('.doc', '.docx', '.pdf')):
                file_path = os.path.join(root, file)

                try:
                    if file.endswith(('.doc', '.docx')):
                        raw_text = read_word_document(file_path)  # You need to implement this function
                    elif file.endswith('.pdf'):
                        raw_text = read_pdf_document(file_path)  # You need to implement this function

                    print(f"Processed document: {file_path}")
                    df = df._append({'filepath': file_path, 'text': raw_text}, ignore_index=True)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

    if df.empty:
        print("No valid documents found.")
        return df

    # Generate embeddings using the get_embedding function
    df['embedding'] = df['text'].astype(str).apply(get_embedding)

    return df




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


def read_file_as_raw_text(file_path):
    """Reads a file and returns its contents as a raw string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."


def read_text_from_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content

source_code = ''


def get_completion(text, script=source_code):
    completion = openai.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": "You take python, javascript, css, html, and sql code as input "
                                          "complete/improve/remove errors from the code, "
                                          "and return the finished code as output. If there is something that could "
                                          "be added to the file to make it better, "
                                          "attempt to integrate it into the code."
                                          f"The code in its entirety is given below:\n{script}"},
            {"role": "user", "content": f"{text}"}
        ]
    )

    result = completion.choices[0].message.content
    log(f"\nCompletion: \nPrompt: {text}\nResult: {result}")
    return result


def create_excel_file(filepath):
    # Save the DataFrame to an Excel file
    df = get_source_code(Path())

    df.to_excel(filepath, index=False, header=False, engine='openpyxl')
    return df


def create_excel_file_text(target_directory, filepath):
    # Save the DataFrame to an Excel file
    df = get_document_text(target_directory)

    df.to_excel(filepath, index=False, header=False, engine='openpyxl')
    return df


def save_source():
    global source_code
    filepath = Path('code/source_code.txt')
    source_code = get_source_code(Path())
    source_code = '\n'.join(source_code)
    num_tokens(source_code)
    save_text_to_file(source_code, filepath)


def create_embeddings_of_self():
    create_excel_file('../llm/embeddings/code_metadata.xlsx')
    flask_embeddings.create_embedding_df('../llm/embeddings/code_metadata.xlsx',
                                         '../llm/embeddings/code_metadata.csv')

def create_embeddings_of_text(target, name):
    create_excel_file_text(target, f'../llm/embeddings/{name}.xlsx')
    flask_embeddings.create_embedding_df(f'../llm/embeddings/{name}.xlsx',
                                         f'../llm/embeddings/{name}.csv')


def relatedness(prompt):
    rel = flask_embeddings.relatedness_score(prompt)
    print(rel)
    return rel

#df = read_embedding('embeddings/resume_test.csv')

#print(df)
#answer = ask_familiar("explain this code", df=df, print_message=True, conversation_id='conversation-1727902220357-g6xwoelao')
#print(answer)


#create_embeddings_of_text('../llm/knowledge_sources/personal', 'resume_test')
#create_embeddings_of_self()


def save_embeddings(directory, output_path):
    df = get_document_text(directory)  # For processing documents in a directory
    print(df.head())
    df.to_csv(output_path, index=False)


directory = "knowledge_sources/personal"
output_path = "embeddings/resume_test.csv"
#save_embeddings(directory, output_path)

#df = read_embedding('embeddings/resume_test.csv')
#rint(df)
#answer = ask("talk to me about this resume", df=df, print_message=True, conversation_id='conversation-1727902220357-g6xwoelao')
#print(answer)

