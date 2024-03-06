from database_connection import Database_connector
from embedder import Embedder
from chat import Chat
from dotenv import load_dotenv
from logger import Logger
import os
import streamlit as st
from chunker import Chunker
from langchain_core.documents import Document
from scoreRetriever import ScoreRetriever
from math import exp
import openai
import os
import pandas as pd
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken
from dotenv import load_dotenv
import streamlit as st
from langchain.chat_models import ChatOpenAI
from sentence_transformers import CrossEncoder
from BM25_retriever import BM25_Retriever
from langchain.retrievers import BM25Retriever
from Hybrid_search import HybridSearch



def test_chat_class():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    database=database_connection.get_db()
    #chat=Chat(database_connection)
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
    st.write("-------------APP----")
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

    llm = ChatOpenAI(
            temperature=0,
            max_tokens=800,
            model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        )

    #print(type(database_connection.get_db()))
    #print(type(database_connection.get_collection()))
    #print(type(llm))

    #CrossEncoderWrapper()
    scoreRetriver=ScoreRetriever(database_connection=database_connection, llm=llm)
    chat=Chat(scoreRetriver)
    chat.chat()
    '''
    database_elements=database_connection.get_all_documents_only()
    documents_from_db=database_elements['documents']
    first_ten_element=documents_from_db[:10]

    
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AOI_KEY")
    client=openai.OpenAI()
    tokens = [" Yes", " No"]
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    ids = [tokenizer.encode(token) for token in tokens]
    scoreRetriver=ScoreRetriever(client=client, tokenizer=tokenizer, tokens=tokens, ids=ids)
    result=scoreRetriver.get_relevance_for_all_documents(first_ten_element, "tabelle gestionali")
    st.write(result)

    st.write(database_elements)
    st.write(type(database_elements['documents']))
    #st.write("Prima del ciclo")
    for database_document in database_elements['documents']:
        print(database_document)
    #    print_test(database_document)
        #st.write(type(database_document))
        #st.write(database_document)
    '''

def test_score_retriever():
    
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AOI_KEY")
    client=openai.OpenAI()
    tokens = [" Yes", " No"]
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    ids = [tokenizer.encode(token) for token in tokens]
    scoreRetriver=ScoreRetriever(client=client, tokenizer=tokenizer, tokens=tokens, ids=ids)
    scoreRetriver.get_ids()

def test_bm25():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    documents=database_connection.get_all_documents()
    sentences=documents['documents']
    st.write(sentences)
    BM25_retriever=BM25_Retriever(sentences)
    retrieved_documents=BM25_retriever.get_relevant_documents("Tabelle gestionali")
    st.write("retrieved documetns")
    st.write(retrieved_documents)

    llm = ChatOpenAI(
            temperature=0,
            max_tokens=800,
            model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        )
    scoreRetriver=ScoreRetriever(database_connection=database_connection, llm=llm)
    scoreRetriver.get_relevant_documents("Tabelle gestionali")


def test_hybrid_search():
    database_connection=Database_connector("localhost", 8000)
    database_connection.connect()
    embedder= Embedder()
    database_connection.get_or_create_collection("RAG", embedder)
    documents=database_connection.get_all_documents()
    sentences=documents['documents']
    documents=[Document(page_content=sentence) for sentence in sentences]
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k =  4
    llm = ChatOpenAI(
            temperature=0,
            max_tokens=800,
            model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        )
    scoreRetriver=ScoreRetriever(database_connection=database_connection, llm=llm)
    hybrid_search=HybridSearch(BM25_retriever=bm25_retriever, scoreRetriever=scoreRetriver)
    chat=Chat(hybrid_search)
    chat.chat()

if __name__ == '__main__':
    #test_score_retriever()
    #test_get_answers_questions("Gestionale")
    #get_all_elements()
    #test_bm25()
    test_hybrid_search()
    
    #    remove_elements()


    #page_titles = ['Accise', 'BPM', 'Conferimenti', 'IWine', 'Mobile', 'Progetti', 'Produzione', 'ESSENZIA_WS', 'Documenti_Ext', 'Wine', 'Essenzia8', 'Essenzia11']
    #test_get_content_page("Accise")
    #test_chat_class()