from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel
from scoreRetriever import ScoreRetriever
from langchain_community.document_transformers import (
    LongContextReorder
)
import streamlit as st

class HybridSearch(BaseRetriever, BaseModel):
    BM25_retriever: BM25Retriever
    scoreRetriever: ScoreRetriever


    def get_relevant_documents(self, query):
        reordering = LongContextReorder()
        ensemble_retriever = EnsembleRetriever(retrievers=[self.BM25_retriever, self.scoreRetriever],weights=[0.4, 0.6])
        docs = ensemble_retriever.get_relevant_documents(query)
        reordered_docs = reordering.transform_documents(docs)
        #st.write("final docs")
        #st.write(reordered_docs)
        #documents = [Document(page_content=combined_text) for combined_text in reordered_docs]
        documents=reordered_docs[:4]
        st.write("hybrid search documents")
        st.write(documents)
        return documents

