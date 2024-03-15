from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel
from langchain_community.document_transformers import (
    LongContextReorder
)
from database_connection import Database_connector

class Not_LITM_retriever(BaseRetriever, BaseModel):
    #questo glielo passso quando lo invoco mettendo attributo=attributo_passato
    database_connection: Database_connector

    def get_relevant_documents(self, query):

        retrieved_document=self.get_documents_by_semantic_search(query)
        #Lost in the middle problem
        reordered_docs=self.__lost_in_middle_problem(retrieved_document)
        return reordered_docs
        
    def get_documents_by_semantic_search(self, text_query):
        retriever = self.database_connection.get_retriever_by_semantic_search()
        result =retriever.get_relevant_documents(text_query)
        return result

    def __lost_in_middle_problem(delf, reranked_docs):
        reordering = LongContextReorder()
        reordered_docs = reordering.transform_documents(reranked_docs)
        return reordered_docs