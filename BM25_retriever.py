#from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
import streamlit as st
from langchain_community.document_transformers import (
    LongContextReorder
)

class BM25_Retriever:

    def __init__(self, senteces):
        documents=self.__convert_to_document(senteces)
        self.bm25_retiever=BM25Retriever.from_documents(documents)
        self.bm25_retiever.k=4
    
    def __convert_to_document(self, senteces):
        documents=[Document(page_content=sentence) for sentence in senteces]
        st.write(documents)
        return documents
    
    def get_relevant_documents(self, query):
        return self.bm25_retiever.get_relevant_documents(query)
    
    def __lost_in_middle_problem(delf, docs):
        reordering = LongContextReorder()
        #questo è quello che devo passare all'llm
        #prima guardare cosa gli restituisco con get_documents_by_semantic_search,
        #ovvero quello di default e poi modificare reordered_docs opportunamente
        reordered_docs = reordering.transform_documents(docs)
        documents = [Document(page_content=combined_text) for combined_text in reordered_docs]
        #MESSO SOLO PER LIMITARE IL COSTO
        #DEVE ESSERE UGUALE AL MUMERO DI DOCUMENTI RESTITUITI DALLO SCORE RETRIEVER
        documents=documents[:4]
        return documents
