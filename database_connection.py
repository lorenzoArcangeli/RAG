import chromadb
from embedder import Embedder
from langchain_community.vectorstores import Chroma
import streamlit as st
from langchain.schema import Document
import time




class Database_connector:

    def __init__(self, host, port):
        self.__host=host
        self.__port=port
        self.__chroma_client=None
        self.__collection=None
        self.__db=None

    def connect(self):
        self.__chroma_client= chromadb.HttpClient(host='localhost', port=8000)
        #self.__chroma_client.delete_collection(name="RAG")
    
    #da aggiungere il controllo se già esiste
    def create_collection(self, collection_name, embedder):
        self.__collection = self.__chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} # l2 is the default
        )
        self.__db=Chroma(
            client=self.__chroma_client,
            collection_name=collection_name,
            # non lo so se lo devo passare oppure no
            embedding_function=embedder.get_embedding_funciont()
        )
        
    #anche qui mettere il controllo
    def get_collection(self, collection_name, embedder):
        self.__collection = self.__chroma_client.get_collection(name=collection_name)
        self.__db=Chroma(
            client=self.__chroma_client,
            collection_name=collection_name,
            # non lo so se lo devo passare oppure no
            embedding_function=embedder.get_embedding_funciont()
        )

    def get_or_create_collection(self, collection_name, embedder):
        self.__collection = self.__chroma_client.get_or_create_collection(name=collection_name)
        self.__db=Chroma(
            client=self.__chroma_client,
            collection_name=collection_name,
            # non lo so se lo devo passare oppure no
            embedding_function=embedder.get_embedding_funciont()
        )

    #anche qui mettere il controllo
    def get_vector_amount_in_db(self):
        return self.__collection.count()

    def add_elements_to_collection(self, chunks, embedder):
        #db = Chroma.from_documents(self.__list_extract_from_dict_test(chunks), embedder.get_embedding_funciont())
        
        if self.__collection==None:
            return False
        result = self.__list_extract_from_dict(chunks)
        combined_sentences_list, combined_sentence_embeddings_list, ids_list = result
        self.__collection.add(
                documents=combined_sentences_list,
                embeddings=combined_sentence_embeddings_list,
                ids=ids_list
            )
        
        return True
    '''
    def __list_extract_from_dict_test(self, chunks):
        # void list
        combined_sentences_list = []

        for chunk in chunks:
            # extract fields
            combined_sentences_list.append(Document(page_content=chunk['combined_sentence']))
        # return lists
        return combined_sentences_list
    '''
    
    def __list_extract_from_dict(self, chunks):
        # void list
        combined_sentences_list = []
        combined_sentence_embeddings_list = []
        ids_list = []

        for chunk in chunks:
            # extract fields
            combined_sentences_list.append(chunk['combined_sentence'])
            #qua è una lista di liste, quindi tocca un attimo modificarlo
            combined_sentence_embeddings_list.append(chunk['combined_sentence_embedding'])
            ids_list.append(str(chunk['id']))
        st.write("LIST TYPE")
        st.write(type(combined_sentence_embeddings_list))
        # return lists
        return combined_sentences_list, combined_sentence_embeddings_list, ids_list

    #mettere il controllo
    def get_retriever_by_semantic_search(self):
        return self.__db.as_retriever(search_kwargs={"k": 10})
    
    def get_db(self):
        return self.__db

    def get_documents_by_semantic_search(self, embedded_query):
        semantic_result=self.__collection.query(
            query_embeddings=embedded_query,
            n_results=10
        )
        # list of document
        return semantic_result

    #probabilmetne non serve
    def get_document_based_on_keyword(self, keyword):
        keyword_where_condition=self.__get_multiple_where_condition(keyword)
        keyword_result=self.__collection.get(
            where=keyword_where_condition
        )
        # list of document
        return keyword_result

    def __get_multiple_where_condition(self, keyword):
        or_clause = []
        # insert string ad dictinary in the list
        for parola in lista_ricerche:
            or_clause.append({"contains": parola})
        # final dictionary
        where_clause = {"$or": or_clause}

    def get_all_documents(self):
        #by default it returns only documents and ids, I added the embeddings 
        return self.__collection.get(include=['embeddings', 'documents'])
    
    def remove_elements(self):
        numeri = [str(numero) for numero in range(17, 35)]
        self.__collection.delete(
            ids=numeri
        )

    '''
    where_clause = {
        "$or" : [
            {"contains" : "first_string"}, 
            {"contains" : "second_string"}, 
        ]
    }

    results = collection.query(
        query_texts="phone manufacturers", 
        n_results=5, 
        where = where_clause
    )
    '''
        
