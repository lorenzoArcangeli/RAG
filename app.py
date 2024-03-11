from database_connection import Database_connector
from embedder import Embedder
#from test.chat import Chat
from dotenv import load_dotenv
from logger import Logger
import os
import streamlit as st
from chunker import Chunker
from langchain_core.documents import Document
from UI_chat import UIChat


def test_chat_class():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database=database_connection.get_db()
    chat=Chat(database)
    chat.chat()

def test_get_content_page(page_title):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    page_json=logger.get_content_page(page_title)
    st.write(page_json['query']['pages'][0]['revisions'][0]['slots']['main']['content'])
    vector_amount_in_db=database_connection.get_vector_amount_in_db()
    st.write(vector_amount_in_db)
    chunker=Chunker(vector_amount_in_db, embedder)
    docs=page_json['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    document_chunks_class=chunker.get_document_chunks([Document(page_content=docs)], page_title)
    st.write(document_chunks_class)
    database_connection.add_elements_to_collection(document_chunks_class, embedder)
    database_elements=database_connection.get_all_documents()
    st.write(database_elements)

def test_get_answers_questions(page_title):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    page_json=logger.get_content_page(page_title)
    st.write(page_json['query']['pages'][0]['revisions'][0]['slots']['main']['content'])
    vector_amount_in_db=database_connection.get_vector_amount_in_db()
    st.write(vector_amount_in_db)
    chunker=Chunker(vector_amount_in_db, embedder)
    docs=page_json['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    document_aq_class=chunker.get_answers_questions_test([Document(page_content=docs)])
    st.write(document_aq_class)

def remove_elements():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database_connection.remove_elements()
    database_elements=database_connection.get_all_documents()
    st.write(database_elements)

def get_all_elements():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database_elements=database_connection.get_all_documents()
    st.write(database_elements)

def add_pages(page_title):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    page_json=logger.get_content_page(page_title)
    st.write(page_json)
    st.write(page_json['query']['pages'][0]['revisions'][0]['slots']['main']['content'])
    vector_amount_in_db=database_connection.get_vector_amount_in_db()
    st.write(vector_amount_in_db)
    chunker=Chunker(vector_amount_in_db, embedder)
    chunks=chunker.get_document_chunks([Document(page_content=page_json['query']['pages'][0]['revisions'][0]['slots']['main']['content'])], "OFFERTE_CLIENTI")
    st.write(chunks)
    database_connection.add_elements_to_collection(chunks)
    st.write(database_connection.get_all_documents())

def get_pages_with_metadata(page_title):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    page_json=logger.test_json(page_title)  
    vector_amount_in_db=database_connection.get_vector_amount_in_db()
    st.write(vector_amount_in_db)
    chunker=Chunker(vector_amount_in_db, embedder)
    last_version=logger.get_last_version(page_json)
    chunks=chunker.get_document_chunks([Document(page_content=last_version['slots']['main']['content'])], page_title, last_version['sha1'])
    st.write(chunks)
    metadata=database_connection.get_metadata(chunks)
    st.write(metadata)
    combined_sentences_list, combined_sentence_embeddings_list, uuid_list=database_connection.list_extract_from_dict(chunks)
    st.write(uuid_list)
    database_connection.add_elements_to_collection(chunks)
    result=database_connection.get_all_documents()
    st.write(result)

def add_list_of_pages():
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    page_titles=["Gestionale", "IWine", "Wine"]
    for page_title in page_titles:
        page_json=logger.test_json(page_title)  
        vector_amount_in_db=database_connection.get_vector_amount_in_db()
        st.write(vector_amount_in_db)
        chunker=Chunker(vector_amount_in_db, embedder)
        last_version=logger.get_last_version(page_json)
        chunks=chunker.get_document_chunks([Document(page_content=last_version['slots']['main']['content'])], page_title, last_version['sha1'])
        database_connection.add_elements_to_collection(chunks)
    result=database_connection.get_all_documents()
    st.write(result)

def get_complete_json():
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    complete_json=logger.test_json()
    st.write(complete_json)
    versions=complete_json['query']['pages'][0]['revisions']
    last_version=versions[-1]
    st.write(last_version)

def get_pages():
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    logger.get_page_info()

def UI_chat():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database=database_connection.get_db()
    chat=UIChat(database)
    chat.chat()

if __name__ == '__main__':
    #get_pages_with_metadata("Gestionale")
    add_list_of_pages()
    #UI_chat()
    #add_pages_with_metadata("Gestionale")
    #get_complete_json()
    #get_pages()
    #test_chat_class()
    #add_pages("OFFERTE_CLIENTI")
    #get_all_elements()
    #test_get_answers_questions("Gestionale")
    #test_chat_class()
    #get_all_elements()
    
    
    #    remove_elements()


    #page_titles = ['Accise', 'BPM', 'Conferimenti', 'IWine', 'Mobile', 'Progetti', 'Produzione', 'ESSENZIA_WS', 'Documenti_Ext', 'Wine', 'Essenzia8', 'Essenzia11']
    #test_get_content_page("Accise")
    #test_chat_class()