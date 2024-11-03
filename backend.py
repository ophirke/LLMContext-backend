import iris
import os
import numpy as np

from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

APP = FastAPI()
APP.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
)


def list_to_csp(lst):
    return "(" + ", ".join([str(x) for x in lst]) + ")"


EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
TABLE_NAME = 'potato_test'
EMBED_DIM = 384
TABLE_DESC_DICT = {
    "user_id": {'type': 'INT', 'placeholder': '?'},
    "url": {'type': 'VARCHAR(1024)', 'placeholder': '?'},
    "context_text": {'type': 'VARCHAR(4096)', 'placeholder': '?'},
    "context_vector": {'type': f"VECTOR(DOUBLE, {EMBED_DIM})", 'placeholder': 'TO_VECTOR(?)'}
}
TABLE_DESC = list_to_csp([k + ' ' + v['type'] for k, v in TABLE_DESC_DICT.items()])

USERNAME = 'demo'
PASSWORD = 'demo'
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = '1972'
namespace = 'USER'
CONNECTION_STRING = f"{hostname}:{port}/{namespace}"

DEFAULT_TOPK = 3


def split_context_into_chunks(context_text: str):
    documents = [Document(page_content=context_text)]
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100, separator=' ')
    docs = text_splitter.split_documents(documents=documents)
    return [doc.page_content for doc in docs]


def delete_table(sql_cursor, table_name):
    sql_cursor.execute(f"DROP TABLE {table_name}")


def create_table_if_not_exists(sql_cursor, table_name, table_schema):
    sql_cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} {table_schema}")


def insert_data(sql_cursor, table_name: str, data: dict):
    colstring = list_to_csp(data.keys())
    valstring = list_to_csp([TABLE_DESC_DICT[k]['placeholder'] for k in data.keys()])
    vals = tuple(data[k] for k in data.keys())
    query = f"INSERT INTO {table_name} {colstring} VALUES {valstring}"
    sql_cursor.execute(query, vals)


def embed_strings(strings: list[str]):
    return [EMBED_MODEL.encode(s) for s in strings]


def add_context_for_user(user_id: int, url: str, context: str):
    # put context into table
    print(f"Connecting to IRIS at {CONNECTION_STRING}")
    with iris.connect(CONNECTION_STRING, USERNAME, PASSWORD) as conn:
        print("Connected to IRIS")
        sql_cursor = conn.cursor()
        context_chunks = split_context_into_chunks(context)
        embedded_context_chunks = embed_strings(context_chunks)
        for context_text, context_vector in zip(context_chunks, embedded_context_chunks):
            insert_data(sql_cursor, TABLE_NAME, {
                'user_id': user_id,
                'url': url,
                'context_text': context_text,
                'context_vector': str(list(context_vector))
            })


def vector_search(sql_cursor, user_id: int, query_vector: np.ndarray, topk: int = DEFAULT_TOPK):
    # Define the SQL query with placeholders for the vector and limit
    sql_query = f"""
        SELECT TOP ? context_text, VECTOR_DOT_PRODUCT(context_vector, TO_VECTOR(?)) as score
        FROM {TABLE_NAME}
        WHERE user_id = ?
        ORDER BY score DESC
    """

    # Execute the query with the number of results and search vector as parameters
    sql_cursor.execute(sql_query, (topk, str(list(query_vector)), user_id))

    # Fetch the results and print them
    return sql_cursor.fetchall()


def get_context_for_user(user_id: int, question: str):
    # put context into table
    print(f"Connecting to IRIS at {CONNECTION_STRING}")
    with iris.connect(CONNECTION_STRING, USERNAME, PASSWORD) as conn:
        print("Connected to IRIS")
        sql_cursor = conn.cursor()
        question_vector = embed_strings([question])[0]
        top_context_texts = vector_search(sql_cursor, user_id, question_vector)
    return top_context_texts


def maybe_create_table():
    print(f"Connecting to IRIS at {CONNECTION_STRING}")
    with iris.connect(CONNECTION_STRING, USERNAME, PASSWORD) as conn:
        print("Connected to IRIS")
        sql_cursor = conn.cursor()
        create_table_if_not_exists(sql_cursor, TABLE_NAME, TABLE_DESC)


@APP.post("/post_context")
async def post_context(user_id: int, url: str, context: str):
    add_context_for_user(user_id, url, context)


@APP.get("/get_context")
async def get_context(user_id: int, question: str):
    return get_context_for_user(user_id, question)

