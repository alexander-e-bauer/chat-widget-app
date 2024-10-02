import os
from pathlib import Path
import pandas as pd

import tiktoken
import openai
import config
import xyz.llm.embedding_model as flask_embeddings
log = config.log




def num_tokens(text):
    encoding = tiktoken.encoding_for_model('gpt-4o')
    encoding = encoding.encode(text, disallowed_special=())
    print(len(encoding))
    return len(encoding)


def save_text_to_file(text, file_path):
    file_path = Path(file_path)
    with open(file_path, 'w') as file:
        file.write(text)


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

def create_embeddings_of_text(name):
    create_excel_file(f'../llm/embeddings/{name}.xlsx')
    flask_embeddings.create_embedding_df(f'../llm/embeddings/{name}.xlsx',
                                         f'../llm/embeddings/{name}.csv')


def relatedness(prompt):
    rel = flask_embeddings.relatedness_score(prompt)
    print(rel)
    return rel


#answer = flask_embeddings.ask("explain this code", print_message=True)
#print(answer)

#create_embeddings_of_self()


