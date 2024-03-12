import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from decorate_document import Document_decorator
import streamlit as st

class Chunker:
    
    def __init__(self, embedder):
        #create embedder object
        self.__embedder=embedder
        self.__document_decorator=Document_decorator(self.__embedder)
        self.keyword=None
        self.sha1=None
        
    
    def get_document_chunks(self, document, title, sha1):
        self.sha1=sha1
        # get_page_keyword --> used to add page keyword
        #self.keyword=self.__document_decorator.get_page_keyword(document)
        sentences=self.__create_document_chunks(document)
        # if there is only one chunk in the document
        if len(sentences)<=1:
            sentences[0]['combined_sentence']=sentences[0]['sentence']
            st.write(sentences)
            document_chunks=sentences
            st.write(document_chunks)
        else: 
            distances, sentences = self.__calculate_cosine_distances(sentences)
            indexes_above_treshold_distance=self.__identify_indexes_above_treshold_distance(distances)
            document_chunks=self.__group_chunks(indexes_above_treshold_distance, sentences)
        # get_page_summary --> used to add summery 
        # get_answers_questions --> used to add questions answers
        # add_autoincrement_value --> no more used
        #document_chunks.append(self.__document_decorator.get_page_summary(document, title))
        #document_chunks.extend(self.get_answers_questions(document))
        #document_chunks=self.__document_decorator.add_autoincrement_value(document_chunks, self.vector_amount_in_db)
        document_chunks=self.__document_decorator.remove_index_and_simple_sentece_from_senteces(document_chunks)
        document_chunks=self.__document_decorator.add_metadata(document_chunks, "web",self.sha1, title)
        return document_chunks

    #METODO DI TEST PER TESTARE L'ESTRAZIONE DI DOMANDE E RISPOSTE
    def get_answers_questions_test(self, document):
        self.keyword=self.__document_decorator.get_page_keyword(document)
        sentences=self.__create_document_chunks(document)
        distances, sentences = self.__calculate_cosine_distances(sentences)
        indexes_above_treshold_distance=self.__identify_indexes_above_treshold_distance(distances)
        document_chunks=self.__group_chunks(indexes_above_treshold_distance, sentences)
        st.write(document_chunks)
        return self.__document_decorator.extract_questions_anwers_from_document(document_chunks)

    def __create_document_chunks(self, document):
        #split document (based on length)
        text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=512, chunk_overlap=50
        )
        docs_split=text_splitter.split_documents(document)
        string_text = [docs_split[i].page_content for i in range(len(docs_split))]
        sentences = [{'sentence': x, 'index' : i} for i, x in enumerate(string_text)]
        # the second argument indicates the number of sentences to combine before and after the current sentence
        sentences = self.__combine_sentences(sentences, 1)
        # emnedding
        embeddings=self.__embedder.do_embedding(sentences)
        for i, sentence in enumerate(sentences):
            sentence['combined_sentence_embedding'] = embeddings[i]
        #st.write("sentences")
        #st.write(sentences)
        return sentences

    #buffer size: number of sentence before and after the current one to be joined
    def __combine_sentences(self, sentences, buffer_size):
        for i in range(len(sentences)):
            # create a string for the joined sentences
            combined_sentence = ''
            # add sentences before the current one, based on the buffer size.
            for j in range(i - buffer_size, i):
                # check if the index j is not negative (avoid problem for the first sentence)
                if j >= 0:
                    combined_sentence += sentences[j]['sentence'] + ' '
            # add the current sentence
            combined_sentence += sentences[i]['sentence']

            # add sentences after the current one, based on the buffer size
            for j in range(i + 1, i + 1 + buffer_size):
                # check if the index j is within the range of the sentences list
                if j < len(sentences):
                    combined_sentence += ' ' + sentences[j]['sentence']
            # store the combined sentence in the current sentence dict
            sentences[i]['combined_sentence'] = combined_sentence
        return sentences

    def __calculate_cosine_distances(self, sentences):
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]['combined_sentence_embedding']
            embedding_next = sentences[i + 1]['combined_sentence_embedding']
            # calculate cosine similarity
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
            # convert to cosine distance
            distance = 1 - similarity
            # append cosine distance to the list
            distances.append(distance)
            # store distance in the dictionary
            sentences[i]['distance_to_next'] = distance
        return distances, sentences

    def __identify_indexes_above_treshold_distance(self, distances, distance=95):
        # identify the outlier
        # higher percentile --> less chunks
        # lower percentile --> more chunks
        breakpoint_distance_threshold = np.percentile(distances, distance) 
        # Indexes of the chunks with cosine distance above treshold
        # The indices of those breakpoints on the list
        indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold]
        return indices_above_thresh

    def __group_chunks(self, indices, sentences):
        # initialize the start index
        start_index = 0
        # create a list to hold the grouped sentences
        chunks = []
        # iterate through the breakpoints to slice the sentences
        for index in indices:
            # the end index is the current breakpoint
            end_index = index
            # slice the sentence_dicts from the current start index to the end index
            group = sentences[start_index:end_index + 1]
            combined_text = ' '.join([repr(d['sentence']) for d in group])
            chunks.extend(self.__check_len([Document(page_content=combined_text)]))
            start_index = index + 1
        # the last group, if any sentences remain
        if start_index < len(sentences):
            combined_text = ' '.join([repr(d['sentence']) for d in sentences[start_index:]])
            chunks.extend(self.__check_len([Document(page_content=combined_text)]))
        return chunks
    
    def __check_len(self, document):
        # chek if the amount of token id above the limit
        if len(document[0].page_content)*0.75>1024:
            # create chunks
            text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=1024, chunk_overlap=50
            )
            docs_split=text_splitter.split_documents(document)
            # get new embeddings for the new chunks
            return self.__get_new_chunk(len(docs_split), docs_split)
        else:
            #st.write("Sotto i 1024")
            return self.__get_new_chunk(1, document)
    
    def __get_new_chunk(self, leng, document):
        splitted_chunks = []
        # get strings from documents
        string_text = [document[i].page_content for i in range(leng)]
        sentences = [{'sentence': x, 'index' : i} for i, x in enumerate(string_text)]
        #keyword of the page
        #sentences = [{'sentence': f"{"informazioni correlate: "}{self.keyword}{"\n\n\n"} {x['sentence']}", 'index': x['index']} for x in sentences]
        sentences = [{'sentence': f"{x['sentence']}", 'index': x['index']} for x in sentences]
        # get sentence and combined_sentence
        for i in range(len(sentences)):
            combined_sentence = sentences[i]['sentence']
            sentences[i]['combined_sentence'] = combined_sentence
        # get new embeddings for the new chunks
        embeddings=self.__embedder.do_embedding(sentences)
        for i, sentence in enumerate(sentences):
            sentence['combined_sentence_embedding'] = embeddings[i]
        # add the new chunks to the list
        splitted_chunks.extend(sentences)
        return splitted_chunks