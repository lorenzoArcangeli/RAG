import langchain
import langchain_community
import sentence_transformers
from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel
from embedder import Embedder
from sentence_transformers import CrossEncoder
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from sentence_transformers import CrossEncoder
from langchain_community.document_transformers import (
    LongContextReorder
)
import streamlit as st
from database_connection import Database_connector
from langchain.schema import Document

from cost_estimator import costEsimator


class LineList(BaseModel):
    lines: list[str] = Field(description="Lines of text")

'''
class CrossEncoderWrapper:
    st.write("ciao")
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    @staticmethod
    def get_encoder():
        return CrossEncoderWrapper.cross_encoder
'''
class LineListOutputParser(PydanticOutputParser):
    def __init__(self) -> None:
        super().__init__(pydantic_object=LineList)

    def parse(self, text: str) -> list[str]:
        lines = text.variablestrip().split("\n")
        return lines
    
#Query Extentions --> from one query to five to get more documents from db
#GUARDARE LA DIFFERENZA TRA BY ENCODER E CROSS ENCODER

class ScoreRetriever(BaseRetriever, BaseModel):
    #questo glielo passso quando lo invoco mettendo attributo=attributo_passato
    database_connection: Database_connector # gli devo passare la collezione e il db
    llm: langchain.chat_models.openai.ChatOpenAI
    #cross_encoder: sentence_transformers.cross_encoder

    def get_relevant_documents(self, query):

        unique_contents=self.__query_expansion(query)

        #CROSS ENCODER RE-RANKING
        reranked_docs=self.__cross_encoder_re_ranking(unique_contents, query)

        '''
        #Lost in the middle problem
        reordered_docs=self.__lost_in_middle_problem(reranked_docs)
        '''
        reordered_docs=reranked_docs[:4]
        st.write(reordered_docs)
        return reordered_docs
        

    
    def __lost_in_middle_problem(delf, reranked_docs):
        reordering = LongContextReorder()
        #questo è quello che devo passare all'llm
        #prima guardare cosa gli restituisco con get_documents_by_semantic_search,
        #ovvero quello di default e poi modificare reordered_docs opportunamente
        reordered_docs = reordering.transform_documents(reranked_docs)

        #prova per veder il costo
        stringa_unificata = ''.join(reordered_docs)
        costEstimator=costEsimator()
        token=costEstimator.count_tokens(stringa_unificata)
        st.write("---------------COST--------------------")
        st.write(costEstimator.calculate_cost(token))
        documents = [Document(page_content=combined_text) for combined_text in reordered_docs]
        #MESSO SOLO PER LIMITARE IL COSTO
        #DEVE ESSERE UGUALE AL MUMERO DI DOCUMENTI RESTITUITI DAL BM25
        documents=documents[:4]
        return documents

    def __cross_encoder_re_ranking(self, unique_contents, query):
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        #zip query and documents and calculate de score
        pairs = []
        for doc in unique_contents:
            pairs.append([query, doc])
        st.write("pre predict")
        #st.write(CrossEncoderWrapper.get_encoder())
        #scores = CrossEncoderWrapper.get_encoder().predict(pairs)
        scores=cross_encoder.predict(pairs)
        st.write("post predict")
        scored_docs = zip(scores, unique_contents)
        sorted_docs = sorted(scored_docs, reverse=True)
        reranked_docs = [doc for _, doc in sorted_docs][0:10]
        return reranked_docs


    #def __setp_back_prompting(self, query):


    def __query_expansion(self, query):
        #output_parser = LineListOutputParser()

        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""Sei un AI language model assistant. Il tuo compito è quello di generare quattro
            diverse versioni della domanda data dall'utente per recuperare i documenti pertinenti da un
            database vettoriale. Generando più prospettive sulla domanda dell'utente, il vostro obiettivo è quello di aiutare
            l'utente a superare alcune delle limitazioni della ricerca of the distance-based similarity
            Fornisce queste domande alternative separate da newlines. Fornisce solo la query, nessuna numerazione.Insersci nella prima riga la query originale che ricevi in input
            (solo la domanda originale, niente altro) senza separazione con la riga sottostante.
            Non aggiungere la doppia interruzione di riga. 
            Il template dell'output deve essere il seguente:
            query originale
            query 1
            query 2
            query 3
            query 4
            query 5
            Domanda originale: {question}""",
        )

        llm_chain = LLMChain(llm=self.llm, prompt=QUERY_PROMPT)
        st.write(query)
        queries = llm_chain.invoke(query)
        queries = queries.get("text")
        queries_splitted = queries.split("\n")
        st.write(queries_splitted)
        for query in queries_splitted:
            st.write(query)
        #questa guardarla perchè force ce da cambiarla
        docs = [self.get_documents_by_semantic_search(query) for query in queries_splitted]
        st.write("documents retrieves")
        st.write(docs)
        
        #TODO: MODIFICARE QUESTO
        unique_contents = set()
        unique_docs = []
        for sublist in docs:
            for doc in sublist:
                if doc.page_content not in unique_contents:
                    unique_docs.append(doc)
                    unique_contents.add(doc.page_content)
        unique_contents = list(unique_contents)
        return unique_contents
        
        
    

    def get_documents_by_semantic_search(self, text_query):
        st.write("query")
        st.write(text_query)
        retriever = self.database_connection.get_retriever_by_semantic_search()
        result =retriever.get_relevant_documents(text_query)
        result=result[:5]
        st.write("get_relevant_documents result")
        st.write(result)
        return result
        '''
        st.write("query")
        st.write(text_query)
        embedder=Embedder()
        embedded_query=embedder.embed_query(text_query)
        semantic_result=self.database_connection.get_collection().query(
            query_embeddings=embedded_query,
            n_results=5,
            include=['documents']
        )
        st.write(semantic_result['documents'])
        # list of document
        return semantic_result['documents']
        '''
        
'''

class ScoreRetriever(BaseRetriever, BaseModel):
    #questo glielo passso quando lo invoco mettendo attributo=attributo_passato
    database_connection: Database_connector # gli devo passare la collezione e il db
    llm: langchain.chat_models.openai.ChatOpenAI
    #cross_encoder: sentence_transformers.cross_encoder
    

    def get_relevant_documents(self, query):

        #Query Expansion
        
        query = "Do you offer vegetarian food?"
        self.llm = ChatOpenAI(
            temperature=0,
            max_tokens=800,
            model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
        )
        

        unique_contents=self.__query_expansion(query)

        #CROSS ENCODER RE-RANKING
        reranked_docs=self.__cross_encoder_re_ranking(unique_contents, query)

        #Lost in the middle problem
        reordered_docs=self.__lost_in_middle_problem(reranked_docs)
        st.write(reordered_docs)
        return reordered_docs
        

    def __lost_in_middle_problem(delf, reranked_docs):
        reordering = LongContextReorder()
        #questo è quello che devo passare all'llm
        #prima guardare cosa gli restituisco con get_documents_by_semantic_search,
        #ovvero quello di default e poi modificare reordered_docs opportunamente
        reordered_docs = reordering.transform_documents(reranked_docs)
        return reordered_docs


    def __cross_encoder_re_ranking(self, unique_contents, query):
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        #zip query and documents and calculate de score
        pairs = []
        for doc in unique_contents:
            pairs.append([query, doc])
        st.write("pre predict")
        #st.write(CrossEncoderWrapper.get_encoder())
        #scores = CrossEncoderWrapper.get_encoder().predict(pairs)
        scores=cross_encoder().predict(pairs)
        st.write("post predict")
        scored_docs = zip(scores, unique_contents)
        sorted_docs = sorted(scored_docs, reverse=True)
        reranked_docs = [doc for _, doc in sorted_docs][0:10]
        return reranked_docs

    def __query_expansion(self, query):
        #tramite questo mi prendo tutte le query simili che mi tira fuori e le metto riga per riga
        output_parser = LineListOutputParser()
        #tradurlo in italiano
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""Sei un AI language model assistant. Il tuo compito è quello di generare cinque
            diverse versioni della domanda data dall'utente per recuperare i documenti pertinenti da un
            database vettoriale. Generando più prospettive sulla domanda dell'utente, il vostro obiettivo è quello di aiutare
            l'utente a superare alcune delle limitazioni della ricerca of the distance-based similarity
            Fornisce queste domande alternative separate da newlines. Fornisce solo la query, nessuna numerazione.
            Domanda originale: {question}""",
        )
        llm_chain = LLMChain(llm=self.llm, prompt=QUERY_PROMPT)
        #qui ho le liste dell query --> nel caso lo potrei anche stampare all'inizop
        queries = llm_chain.invoke(query)
        queries = queries.get("text")
        #questa guardarla perchè force ce da cambiarla
        docs = [self.get_documents_by_semantic_search(query) for query in queries]
        st.write("documents retrieves")
        st.write(docs)
        unique_contents = set()
        unique_docs = []
        #Acendo generato 5 query da 1 forse ci sono dei documenti duplicati e quindi li elimino
        for sublist in docs:
            for doc in sublist:
                if doc.page_content not in unique_contents:
                    unique_docs.append(doc)
                    unique_contents.add(doc.page_content)
        unique_contents = list(unique_contents)
        return unique_contents

            
    def get_documents_by_semantic_search(self, text_query):
        embedder=Embedder()
        embedded_query=embedder.embed_query(text_query)
        semantic_result=self.database_connection.get_collection().query(
            query_embeddings=embedded_query,
            n_results=5,
            include=['documents']
        )
        # list of document
        return semantic_result

    def get_relevant_documents(self, query, **kwargs):
        results = self.get_documents_by_semantic_search(query)
        return [doc for doc in results if doc['title'].startswith(self.title)]
    

    
    async def aget_relevant_documents(self, query, **kwargs):
        results = await self.retriever.aget_relevant_documents(query, **kwargs)
        return [doc for doc in results if doc['title'].startswith(self.title)]
 
'''