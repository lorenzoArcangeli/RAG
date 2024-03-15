from database_connection import Database_connector, Check_Page
from embedder import Embedder
#from test.chat import Chat
from dotenv import load_dotenv
from logger import Logger
import os
import streamlit as st
import sys
from chunker_to_delete import Chunker
from langchain_core.documents import Document
from UI_chat import UIChat
from Not_LITM import Not_LITM_retriever
from sectionChunker import sectionChunker

#----TEST METHODS---

#test old content page (without sha1)
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

#test answer questio using doctran --> c'è un problema con le librerie e non funziona pioù
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

#remove elements from db
def remove_elements():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database_connection.remove_elements()
    database_elements=database_connection.get_all_documents()
    st.write(database_elements)

#get elements from db
def get_all_elements():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database_elements=database_connection.get_all_documents()
    st.write(database_elements)

#old method to add pages
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

#current method to add single pages
def get_pages_with_metadata(page_title):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    page_json=logger.complete_json(page_title)  
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

#old method to add list of pages
def add_list_of_pages(page_titles):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    for page_title in page_titles:
        page_json=logger.complete_json(page_title)  
        #vector_amount_in_db=database_connection.get_vector_amount_in_db()
        #st.write(vector_amount_in_db)
        chunker=Chunker(embedder)
        last_version=logger.get_last_version(page_json)
        chunks=chunker.get_document_chunks([Document(page_content=last_version['slots']['main']['content'])], page_title, last_version['sha1'])
        database_connection.add_elements_to_collection(chunks)
    result=database_connection.get_all_documents()
    st.write(result)

#get json with sha1
def get_complete_json():
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    complete_json=logger.complete_json("Registri_Telematici")
    st.write(complete_json)
    versions=complete_json['query']['pages'][0]['revisions']
    last_version=versions[-1]
    st.write(last_version)

#test to verify sha1
def test_check_page_title_sha1(page_title):
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    res, ids=database_connection.check_page_by_title(page_title, "ciao")
    st.write(res)
    st.write(ids)
    elements=database_connection.get_all_documents()
    st.write(elements)
    #c493407923c50830655d1a416e3df11294c06ef7
    '''
    0:"1784a171-9441-4fca-a786-a65d7a135bbd"
    1:"6166e1a0-af60-4554-9c22-901849d7bf75"
    2:"a49ffbaa-7a51-4ec8-b0b5-c43fabee6d5a"
    3:"e3d08ba5-0ee9-44a1-a64f-03467855d5bd"
    '''

# test method to verify get pages method
def get_pages():
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    #logger.get_pages_in_namespace(0)
    logger.get_pages()

#----FUNCTION METHODS---

#delete collection by name
def delete_collection(name):
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    database_connection.delete_collection(name)

def add_list_of_pages_check_sha1(page_titles, page_ids):
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    index=0
    for page_title in page_titles:
        st.write("page")
        st.write(page_title)
        page_json=logger.complete_json_by_id(page_ids[index]) 
        #st.write(page_json)
        last_version=logger.get_last_version(page_json)
        if len(last_version['slots']['main']['content'])>0:
            st.write("page with content")
            st.write(page_title)
            need_embedding, ids=database_connection.check_page_by_id(page_ids[index], last_version['sha1'])
            if need_embedding!=Check_Page.NO_NEED:
                chunker=Chunker(embedder)
                chunks=chunker.get_document_chunks([Document(page_content=last_version['slots']['main']['content'])], page_title, page_ids[index], last_version['sha1'])
                if need_embedding==Check_Page.NEED_EMBEDDING:
                    st.write("NEED_EMBEDDING")
                    database_connection.add_elements_to_collection(chunks)
                else:
                    st.write("MODIFY_EMBEDDING")
                    database_connection.modify_elements_of_collection(chunks, ids)
            st.write(index)
        else:
            st.write("page with no content")
            st.write(page_title)
        index+=1
    result=database_connection.get_all_documents()
    st.write(result)

#current method for UI chat
def UI_chat():
    #localhost --> runno in locale
    #chroma --> se lo runno da dokcer compose 
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    #database=database_connection.get_db()
    not_lost_in_the_middle_retriever=Not_LITM_retriever(database_connection=database_connection)
    chat=UIChat(not_lost_in_the_middle_retriever)
    chat.chat()

def test_section_chunker():
    load_dotenv()
    logger=Logger(os.getenv("USERNAME_APRA"), os.getenv("PASSWORD"), "https://wikidoc.apra.it/essenzia/api.php")
    logger.login()
    page_json=logger.complete_json_by_id(6708) 
    last_version=logger.get_last_version(page_json)
    embedder= Embedder()
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    database_connection.get_or_create_collection("RAG", embedder)
    chunker=sectionChunker(embedder)
    chunks=chunker.get_document_chunks(last_version['slots']['main']['content'], "Varianti Errate", 6708, last_version['sha1'])
    st.write(chunks)
    need_embedding, ids=database_connection.check_page_by_id(6708, last_version['sha1'])
    st.write(need_embedding)
    st.write(ids)



#insert all the web pages
def insert_all_pages():
    #LE PAGINE SENZA CONTESTO VENGONO SCARTATE
    
    with open("Page_titles.txt", 'r') as file:
        # Leggi tutte le righe del file e memorizzale in una lista
        titles = file.readlines()
    with open("Page_ids.txt", 'r') as file:
        # Leggi tutte le righe del file e memorizzale in una lista
        ids = file.readlines()
    correct_titles = [line.strip() for line in titles]
    correct_ids = [line.strip() for line in ids]
    add_list_of_pages_check_sha1(correct_titles, correct_ids)

if __name__ == '__main__':
    #UI_chat()
    test_section_chunker()