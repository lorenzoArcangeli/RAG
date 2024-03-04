from database_connection import Database_connector
from embedder import Embedder
from chat import Chat
from dotenv import load_dotenv
from logger import Logger
import os
import streamlit as st
from chunker import Chunker
from langchain_core.documents import Document


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

if __name__ == '__main__':
    #get_all_elements()
    
    
    #    remove_elements()


    #page_titles = ['Accise', 'BPM', 'Conferimenti', 'IWine', 'Mobile', 'Progetti', 'Produzione', 'ESSENZIA_WS', 'Documenti_Ext', 'Wine', 'Essenzia8', 'Essenzia11']
    #test_get_content_page("Accise")
    test_chat_class()