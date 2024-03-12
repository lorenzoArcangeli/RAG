import chromadb
from langchain_community.vectorstores import Chroma
from enum import Enum

class Check_Page(Enum):
    NEED_MODIFY_EMBEDDING = 1
    NO_NEED = 2
    NEED_EMBEDDING=3

class Database_connector:

    def __init__(self, host, port):
        self.__host=host
        self.__port=port
        self.__chroma_client=None
        self.__collection=None
        self.__db=None

    def connect(self):
        self.__chroma_client= chromadb.HttpClient(host=str(self.__host), port=self.__port)
    
    def create_collection(self, collection_name, embedder):
        self.__collection = self.__chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} # l2 is by default
        )
        self.__db=Chroma(
            client=self.__chroma_client,
            collection_name=collection_name,
            embedding_function=embedder.get_embedding_funciont()
        )

    def get_collection(self, collection_name, embedder):
        self.__collection = self.__chroma_client.get_collection(name=collection_name)
        self.__db=Chroma(
            client=self.__chroma_client,
            collection_name=collection_name,
            embedding_function=embedder.get_embedding_funciont()
        )

    def get_or_create_collection(self, collection_name, embedder):
        self.__collection = self.__chroma_client.get_or_create_collection(name=collection_name)
        self.__db=Chroma(
            client=self.__chroma_client,
            collection_name=collection_name,
            embedding_function=embedder.get_embedding_funciont()
        )

    '''
    era usato prima di inserire l'uuid
    def get_vector_amount_in_db(self):
        return self.__collection.count()
    '''
    def add_elements_to_collection(self, chunks):     
        if self.__collection==None:
            return False
        result = self.list_extract_from_dict(chunks)
        combined_sentences_list, combined_sentence_embeddings_list, uuid_list = result
        metadata=self.get_metadata(chunks)
        self.__collection.add(
                documents=combined_sentences_list,
                embeddings=combined_sentence_embeddings_list,
                metadatas=metadata,
                ids=uuid_list
            )
        return True
    
    def get_metadata(self, chunks):
        # extract metadata from chunks
        metadata_list = [] 
        for chunk in chunks:
            metadata = {
                'type': chunk['type'],
                'sha1': chunk['sha1'],
                'title': chunk['title']
            }
            metadata_list.append(metadata)
        return metadata_list
      
    def list_extract_from_dict(self, chunks):
        # extract lists from chunks
        combined_sentences_list = []
        combined_sentence_embeddings_list = []
        ids_list = []

        for chunk in chunks:
            # extract fields
            combined_sentences_list.append(chunk['combined_sentence'])
            combined_sentence_embeddings_list.append(chunk['combined_sentence_embedding'])
            ids_list.append(str(chunk['uuid']))
        #st.write("LIST TYPE")
        #st.write(type(combined_sentence_embeddings_list))
        return combined_sentences_list, combined_sentence_embeddings_list, ids_list

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

    # non usato
    def get_document_based_on_keyword(self, keyword):
        keyword_where_condition=self.__get_multiple_where_condition(keyword)
        keyword_result=self.__collection.get(
            where=keyword_where_condition
        )
        # list of document
        return keyword_result
    
    def delete_collection(self, collection_name):
        self.__chroma_client.delete_collection(name=collection_name) 

    def check_page(self, page_title, sha1):
        result=self.__collection.get(
            include=['metadatas'],
            where={
                    "title": str(page_title)
                }
        )
        if len(result)==0:
            return Check_Page.NEED_EMBEDDING, None
        else:
            for metadata in result['metadatas']:
                if metadata['sha1']==str(sha1):
                    return Check_Page.NO_NEED, None
        return Check_Page.NEED_MODIFY_EMBEDDING, result['ids']

    def modify_elements_of_collection(self, chunks, ids):
        if self.__collection==None:
            return False
        result = self.list_extract_from_dict(chunks)
        combined_sentences_list, combined_sentence_embeddings_list, uuid_list = result
        metadata=self.get_metadata(chunks)
        self.__collection.update(
                ids=ids,
                documents=combined_sentences_list,
                embeddings=combined_sentence_embeddings_list,
                metadatas=metadata
            )
        return True

    '''
    def __get_multiple_where_condition(self, keyword):
        or_clause = []
        # insert string ad dictinary in the list
        for parola in lista_ricerche:
            or_clause.append({"contains": parola})
        # final dictionary
        where_clause = {"$or": or_clause}
    '''

    def get_all_documents(self):
        #by default it returns only documents and ids, I added the embeddings 
        return self.__collection.get(include=['embeddings', 'documents', 'metadatas'])
    
    # non usato
    def remove_elements(self):
        numeri = [str(numero) for numero in range(17, 35)]
        self.__collection.delete(
            ids=numeri
        )

    '''
    prova per avere clause where composte
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
        
