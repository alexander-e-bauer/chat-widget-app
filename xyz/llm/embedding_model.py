import os
import re
import pandas as pd
from scipy import spatial
import ast
import tiktoken

import config

log = config.log
OAI = config.OAI



embedding_model = OAI.embedding3
# Set display options to show all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



def read_embedding(embedding_path):
    return pd.read_csv(
        embedding_path,
        index_col=0,
        converters={
            'embedding': lambda x: ast.literal_eval(x)
        }
    )


# search function
def strings_ranked_by_relatedness(
        query: str,
        df: pd.DataFrame,
        relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
        top_n: int = 100
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    if df.empty:
        log("DataFrame is empty. Cannot compute relatedness.")
        return [], []

    query_embedding_response = OAI.client.embeddings.create(
        model=embedding_model,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses) if strings_and_relatednesses else ([], [])
    return strings[:top_n], relatednesses[:top_n]


def relatedness_score(text, _df):
    # examples
    strings, relatednesses = strings_ranked_by_relatedness(text, _df, top_n=3)
    for string, relatedness in zip(strings, relatednesses):
        print(f"\n Relatedness: {relatedness=:.3f}\n")
        print(string)
        print()


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


def create_embedding_df(excel_path, embedding_path):
    # Create a new DataFrame to store the text and its embedding
    _df = pd.DataFrame()

    # Read the Excel file and set row 0 as the header
    review_df = pd.read_excel(excel_path, header=None)

    # Now concatenate all the text in each row into a single cell in a new column called 'text'
    _df['text'] = review_df.apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
    _df.reset_index(drop=True, inplace=True)
    # Display the DataFrame with the concatenated column
    print(_df.head())
    # _df = _df.sample(10)
    _df["embedding"] = _df["text"].astype(str).apply(get_embedding)
    print(_df.head())

    _df.to_csv(embedding_path, index=False)


def num_tokens(text: str, model: str = OAI.gpt4o) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
        query: str,
        df: pd.DataFrame,
        model: str = OAI.gpt4o,
        token_budget: int = 3000
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    if df.empty:
        return "DataFrame is empty. Cannot generate message."

    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the Documents provided below to answer the users questions. ' \
                   'Take care to ensure that your answers are based off of reliable information within the source text.'
    question = f"\n\nTask: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nOriginal Code File:\n"""\n{string}\n"""'
        if (
                num_tokens(message + next_article + question, model=model)
                > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def query_message_code(
        query: str,
        df: pd.DataFrame,
        model: str = OAI.gpt4o,
        token_budget: int = 3000
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    if df.empty:
        return "DataFrame is empty. Cannot generate message."

    strings, relatednesses = strings_ranked_by_relatedness(query, df)
    introduction = 'Use the Original Code Files provided below to answer the users questions about the code. ' \
                   'Based on the users input, Generate one single code that ' \
                   'implements an improvement upon the original code' \
                   'take into account the users input and the original code. ' \
                   'take care to ensure that the code is compatable with the original code. ' \
                   'Respond only with the code, do not include any additional information.'
    question = f"\n\nTask: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nOriginal Code File:\n"""\n{string}\n"""'
        if (
                num_tokens(message + next_article + question, model=model)
                > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def ask(
        query: str,
        df: pd.DataFrame,
        conversation_id,
        model: str = OAI.gpt4o,
        print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You are a helpful assistant who researches and discusses provided documents."},
        {"role": "user", "content": message},
    ]
    response = OAI.client.chat.completions.create(
        model=model,
        messages=messages,
        conversation_id=conversation_id,
        temperature=1.9
    )
    response_message = response.choices[0].message.content
    return response_message


def ask_familiar(
        query: str,
        df: pd.DataFrame,
        conversation_id,
        model: str = OAI.gpt4o,
        print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You are a helpful assistant who is trying to get the person whose resume and work "
                                      "is represented in the provided documents a job as a data scientist or web developer. "
                                      "You respond in a professional, witty, and honest manner and "
                                      "provide specific examples whenever possible. Speak in a general manner, as you "
                                      "are open to many opportunities, not just one specific position, and could be "
                                      "contacted by anybody including potential employers. Don't respond with to many "
                                      "words, dont use  verbose grammar, and dont oversell yourself. Don't give out "
                                      "too much information without being prompted to do so."},
        {"role": "user", "content": message},
    ]
    response = OAI.client.chat.completions.create(
        model=model,
        messages=messages,
        conversation_id=conversation_id,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message


def ask_code(
        query: str,
        df: pd.DataFrame,
        model: str = OAI.gpt4o,
        print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message_code(query, df, model=model)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You Complete the users python, javascript, css, and html code "
                                      "and fully Implement New Code if possible"},
        {"role": "user", "content": message},
    ]
    response = OAI.client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message


