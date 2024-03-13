from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_transformers import DoctranQATransformer
import os
from langchain_core.documents import Document
import json
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid

class Document_decorator:

    def __init__(self, embedder):
        self.__embedder=embedder
        self.__llm=ChatOpenAI(model="gpt-3.5-turbo")
    
    def add_metadata(self, sentences, type, sha1, title, id):
        for sentence in sentences:
            sentence['type']=type # web page or pdf
            new_uuid=uuid.uuid4()
            sentence['uuid']=str(new_uuid) # instead of using increment id
            sentence['sha1']=str(sha1) # used to check if the web page/pad has been changed
            sentence['title']=str(title) # used to identify the we
            sentence['id']=str(id)
        return sentences

    def get_page_summary(self, document, page_title):
        #get the summary for the entire page
        PROMPT = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        Sei l'amministratore di un documento in cui sono presenti elementi che che parlano di un argomento simile.
                        Genera un riassunto dettagliato che informerà gli osservatori ciò di cui si parla nel documento.
                        La lunghezza limite del riassunto è di 3000 parole.

                        Un buon riassunto dice di cosa tratta il documento.

                        Ti verrà dato un documento. Questo documento ha bisogno di un riassunto.
                        
                        Esempio:
                        Input: Documento: Greg ama mangiare la pizza
                        Output: Questo documento contiene informazioni sui tipi di cibo che Greg ama mangiare.

                        Rispondi solo con il nuovo riassunto, nient'altro.
                        """,
                    ),
                    ("user", "Determina il rissunto del seguente documento:\n{proposition}"),
                ]
            )
        runnable = PROMPT | self.__llm

        new_chunk_summary = runnable.invoke({
                "proposition": document
        }).content
        summary_header="Quest è il riassunto generale della pagina web relativa a: "+page_title+"\n\n"
        final_summary=summary_header+new_chunk_summary
        summary = {}  # Initialize the summary dictionary
        summary['sentence']=final_summary
        summary['index']=-1 # identify summary
        summary['combined_sentence']=final_summary
        summary_embedding=self.__embedder.do_embedding([summary])
        summary['combined_sentence_embedding']=summary_embedding
        return summary

    def get_page_keyword(self, document):
        #get keyword for the entire page
        PROMPT = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                        Sei l'amministratore di un documento in cui sono presenti elementi che che parlano di un argomento simile.
                        Genera delle parole chiavi che identificano di cosa si tratta all'interno del documento.
                        Genera il numero di parole chiavi che riteni opportune per identificare gli elementi chiave del documento.

                        Delle buone parole chiavi riescono a far capire agli osservatori di cosa parla il documento.

                        Ti verrà dato un documento. Questo documento ha bisogno di parole chiavi.

                        Rispondi solo con le parole chiavi, nient'altro. Non indicare il numero di parole chiavi
                        """,
                    ),
                    ("user", "Determina il rissunto del seguente documento:\n{proposition}"),
                ]
            )
        runnable = PROMPT | self.__llm

        new_chunk_keyword = runnable.invoke({
                "proposition": document
        }).content
        return new_chunk_keyword
    
    # metodo per testare l'estrazione di domande/rispsote
    def extract_questions_anwers_from_document(self, sentences):
        os.environ["OPENAI_API_MODEL"]="gpt-3.5-turbo"
        #Guardare come farlo senza OpenAI
        qa_transformer = DoctranQATransformer()
        questions_answars=[]
        for sentence in sentences:
            document_from_sentence=[Document(page_content=sentence['combined_sentence'])]
            interrogated_document=qa_transformer.transform_documents(document_from_sentence)
            question_answers=json.dumps(interrogated_document[0].metadata, indent=2)
            questions_answers_splitted=self.__split_question_anwer([Document(page_content=question_answers)])
            questions_answers_splitted_list_dict=[]
            for qas in questions_answers_splitted:
                qasd={'combined_sentence': qas}
                qasd={'sentence': qas}
                qasd_emb=self.__embedder.do_embedding([qas])
                qasd['combined_sentence_embedding']=qasd_emb
                questions_answers_splitted_list_dict.append(qasd)
            questions_answars.extend(questions_answers_splitted_list_dict)
            st.write(questions_answars)
        return questions_answars
    
    def __split_question_anwer(self, answers_questions_document):
        #chek if amount of token id above the limit
        if len(answers_questions_document[0].page_content)*0.75>2000:
            #create chunks
            text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=1024, chunk_overlap=50
            )
            docs_split=text_splitter.split_documents(answers_questions_document)
            #get new embeddings for the new chunks
            return [docs_split[i].page_content for i in range(len(docs_split))]
        else:
            return [answers_questions_document[0].page_content]
    
    def remove_index_and_simple_sentece_from_senteces(self, sentences):
        for sentence in sentences:
            # Remove index and sentence field in the list of dictionary
            sentence.pop('index', None)
            sentence.pop('sentence')
        return sentences
    
    '''
    non server più, adesso uso l'uuid
    def add_autoincrement_value(self, sentences, vector_amount_in_db):
        #finiti tutti i testo togliere il +1 in modo che comincia da 0. poi dato che cominci da 0 il numero effettivo sarà già +1
        for index, sentence in enumerate(sentences, vector_amount_in_db+1):
            sentence['id']=index
        return sentences
    '''