import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from decorate_document import Document_decorator
import streamlit as st

class Chunker:
    
    def __init__(self, vector_amount_in_db, embedder):
        #create embedder object
        self.__embedder=embedder
        self.__document_decorator=Document_decorator(self.__embedder)
        self.vector_amount_in_db=vector_amount_in_db
        self.keyword=None
        
    
    def get_document_chunks(self, document, page_title):
        self.keyword=self.__document_decorator.get_page_keyword(document)
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
        #PER QUESTO CI VUOLE L'ACCOUNT A PAGAMENTO
        #document_chunks.append(self.__document_decorator.get_page_summary(document, page_title))
        document_chunks=self.__document_decorator.add_autoincrement_value(document_chunks, self.vector_amount_in_db)
        document_chunks=self.__document_decorator.remove_index_and_simple_sentece_from_senteces(document_chunks)
        return document_chunks

    
    def get_answers_questions(self, document):
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

        sentences = self.__combine_sentences(sentences, 1)

        embeddings=self.__embedder.do_embedding(sentences)
        for i, sentence in enumerate(sentences):
            sentence['combined_sentence_embedding'] = embeddings[i]
        return sentences

    #buffer size: number of sentence before and after the current one to be joined
    def __combine_sentences(self, sentences, buffer_size):
        # Go through each sentence dict
        for i in range(len(sentences)):
            # Create a string that will hold the sentences which are joined
            combined_sentence = ''
            # Add sentences before the current one, based on the buffer size.
            for j in range(i - buffer_size, i):
                # Check if the index j is not negative (to avoid index out of range like on the first one)
                if j >= 0:
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += sentences[j]['sentence'] + ' '
            # Add the current sentence
            combined_sentence += sentences[i]['sentence']

            # Add sentences after the current one, based on the buffer size
            for j in range(i + 1, i + 1 + buffer_size):
                # Check if the index j is within the range of the sentences list
                if j < len(sentences):
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += ' ' + sentences[j]['sentence']
            # Then add the whole thing to your dict
            # Store the combined sentence in the current sentence dict
            sentences[i]['combined_sentence'] = combined_sentence
        
        return sentences

    def __calculate_cosine_distances(self, sentences):
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]['combined_sentence_embedding']
            embedding_next = sentences[i + 1]['combined_sentence_embedding']
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
            # Convert to cosine distance
            distance = 1 - similarity
            # Append cosine distance to the list
            distances.append(distance)
            # Store distance in the dictionary
            sentences[i]['distance_to_next'] = distance
        return distances, sentences

    def __identify_indexes_above_treshold_distance(self, distances, distance=95):
        # identify the outlier
        # higher percentile --> less chunks, lower percentile --> more chunks
        breakpoint_distance_threshold = np.percentile(distances, distance) 
        # Amount of distances above your threshold
        num_distances_above_theshold = len([x for x in distances if x > breakpoint_distance_threshold]) 
        # Indexes of the chunks with cosine distance above treshold
        # The indices of those breakpoints on your list
        indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold]
        return indices_above_thresh

    def __group_chunks(self, indices, sentences):
        # Initialize the start index
        start_index = 0
        # Create a list to hold the grouped sentences
        chunks = []
        # Iterate through the breakpoints to slice the sentences
        for index in indices:
            # The end index is the current breakpoint
            end_index = index
            # Slice the sentence_dicts from the current start index to the end index
            group = sentences[start_index:end_index + 1]
            combined_text = ' '.join([repr(d['sentence']) for d in group])
            chunks.extend(self.__check_len([Document(page_content=combined_text)]))
            start_index = index + 1
        # The last group, if any sentences remain
        if start_index < len(sentences):
            combined_text = ' '.join([repr(d['sentence']) for d in sentences[start_index:]])
            chunks.extend(self.__check_len([Document(page_content=combined_text)]))
        # grouped_sentences now contains the chunked sentences
        return chunks
    
    def __check_len(self, document):
        #chek if amiunt of token id above the limit
        if len(document[0].page_content)*0.75>2000:
            #create chunks
            text_splitter=RecursiveCharacterTextSplitter(
                chunk_size=1024, chunk_overlap=50
            )
            docs_split=text_splitter.split_documents(document)
            #get new embeddings for the new chunks
            return self.__get_new_chunk(len(docs_split), docs_split)
        else:
            return self.__get_new_chunk(1, document)
    
    def __get_new_chunk(self, leng, document):
        splitted_chunks = []
        #get strings from documents
        string_text = [document[i].page_content for i in range(leng)]
        sentences = [{'sentence': x, 'index' : i} for i, x in enumerate(string_text)]

        #keyword of the page
        sentences = [{'sentence': f"{"informazioni correlate: "}{self.keyword}{"\n\n\n"} {x['sentence']}", 'index': x['index']} for x in sentences]
        
        #get sentence and combined_sentence
        for i in range(len(sentences)):
            combined_sentence = sentences[i]['sentence']
            sentences[i]['combined_sentence'] = combined_sentence
        #oaiembeds = OpenAIEmbeddings()
        #get new embeddings for the new chunks
        #embeddings = oaiembeds.embed_documents([x['combined_sentence'] for x in sentences])
        embeddings=self.__embedder.do_embedding(sentences)
        for i, sentence in enumerate(sentences):
            sentence['combined_sentence_embedding'] = embeddings[i]
        #add the new chunks to the list
        splitted_chunks.extend(sentences)
        return splitted_chunks