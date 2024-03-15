import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from decorate_document import Document_decorator
import streamlit as st
import re


class sectionChunker:
    
    def __init__(self, embedder):
        #create embedder object
        self.__embedder=embedder
        self.__document_decorator=Document_decorator(self.__embedder)
        self.keyword=None
        self.sha1=None

    def get_document_chunks(self, content, page_title, page_id, sha1):
        chunks=self.get_sections(content)
        chunks=self.embed_sections(chunks)
        chunks=self.__document_decorator.add_metadata(chunks, "web", sha1,page_title, page_id)
        return chunks

    
    def get_sections(self, content):
        # Find title
        sections = []
        section_titles = re.findall(r'(==+)([^=]+)\1', content)
        #se non ci sono sezioni all'interno della pagina
        if len(section_titles)==0:
            singol_content={'section':content}
            sections.append(singol_content)
        else:
            #st.write(section_titles)
            # Dividi il contenuto in base alle sezioni
            for i in range(len(section_titles)):
                #section_titles[i][0] corrisponde agli ==
                #section_titles[i][1] corrisponde al titolo effettivo
                start_section = content.find(section_titles[i][0] + section_titles[i][1])
                if i < len(section_titles) - 1:
                    end_section = content.find(section_titles[i+1][0] + section_titles[i+1][1])
                #se è l'ultimo titolo basta prendere la lunghezza del chunk
                else:
                    end_section = len(content)
                section_content = content[start_section:end_section]
                #page_content={'section':section_content}
                #sections.append(page_content)
                #st.write(section_content)
                sections.extend(self.check_len([Document(page_content=section_content)]))
        return sections
    

    def check_len(self, document):
        if len(document[0].page_content)*0.75>1024:
            #prima verifico i === altrimenti mi mette il titolo tra il secondo e terzo =
            end_title = document[0].page_content.find('===', document[0].page_content.find('===') + 1)
            if end_title==-1:
                end_title = document[0].page_content.find('==', document[0].page_content.find('==') + 1)
            title=document[0].page_content[:end_title]
            modified_document = document[0].page_content[:end_title] + "parte " +str(1) + document[0].page_content[end_title:]
            # create chunks
            text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=1024, chunk_overlap=50
            )
            docs_split=text_splitter.split_documents([Document(page_content=modified_document)])
            # get new embeddings for the new chunks
            return self.__get_new_chunk(docs_split, title)
        else:
            return self.__get_new_chunk(document)


    def __get_new_chunk(self, splitted_documents, title=""):
        sections=[]
        for index, doc in enumerate(splitted_documents):
            if index >= 1:
                modified_content=title+"parte "+str(index+1)+"\n"+doc.page_content
                doc_section = {'section': modified_content}
                sections.append(doc_section)
            else:
                doc_section = {'section': doc.page_content}
                sections.append(doc_section)
        return sections
    
    def embed_sections(self, sections):
        embeddings=self.__embedder.do_embedding_sections(sections)
        for i, section in enumerate(sections):
            section['embedding'] = embeddings[i]
        return sections
    

