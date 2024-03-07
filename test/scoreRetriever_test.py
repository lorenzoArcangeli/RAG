from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel
from sentence_transformers import CrossEncoder 
import chromadb
from langchain_community.vectorstores import Chroma
from math import exp
import openai
import os
import pandas as pd
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken
from dotenv import load_dotenv
import streamlit as st


class ScoreRetriever(BaseRetriever, BaseModel):
    client: openai.OpenAI
    tokenizer:tiktoken.Encoding
    tokens:list[str]
    ids:list[list[int]]

    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
    def document_relevance(self, query, document):
        prompt='''
            You are an Assistant responsible for helping detect whether the retrieved document is relevant to the query. For a given input, you need to output a single token: "Yes" or "No" indicating the retrieved document is relevant to the query.

            Query: How to plant a tree?
            Document: """Cars were invented in 1886, when German inventor Carl Benz patented his Benz Patent-Motorwagen.[3][4][5] Cars became widely available during the 20th century. One of the first cars affordable by the masses was the 1908 Model T, an American car manufactured by the Ford Motor Company. Cars were rapidly adopted in the US, where they replaced horse-drawn carriages.[6] In Europe and other parts of the world, demand for automobiles did not increase until after World War II.[7] The car is considered an essential part of the developed economy."""
            Relevant: No

            Query: Has the coronavirus vaccine been approved?
            Document: """The Pfizer-BioNTech COVID-19 vaccine was approved for emergency use in the United States on December 11, 2020."""
            Relevant: Yes

            Query: What is the capital of France?
            Document: """Paris, France's capital, is a major European city and a global center for art, fashion, gastronomy and culture. Its 19th-century cityscape is crisscrossed by wide boulevards and the River Seine. Beyond such landmarks as the Eiffel Tower and the 12th-century, Gothic Notre-Dame cathedral, the city is known for its cafe culture and designer boutiques along the Rue du Faubourg Saint-Honoré."""
            Relevant: Yes

            Query: What are some papers to learn about PPO reinforcement learning?
            Document: """Proximal Policy Optimization and its Dynamic Version for Sequence Generation: In sequence generation task, many works use policy gradient for model optimization to tackle the intractable backpropagation issue when maximizing the non-differentiable evaluation metrics or fooling the discriminator in adversarial learning. In this paper, we replace policy gradient with proximal policy optimization (PPO), which is a proved more efficient reinforcement learning algorithm, and propose a dynamic approach for PPO (PPO-dynamic). We demonstrate the efficacy of PPO and PPO-dynamic on conditional sequence generation tasks including synthetic experiment and chit-chat chatbot. The results show that PPO and PPO-dynamic can beat policy gradient by stability and performance."""
            Relevant: Yes

            Query: Explain sentence embeddings
            Document: """Inside the bubble: exploring the environments of reionisation-era Lyman-α emitting galaxies with JADES and FRESCO: We present a study of the environments of 16 Lyman-α emitting galaxies (LAEs) in the reionisation era (5.8<z<8) identified by JWST/NIRSpec as part of the JWST Advanced Deep Extragalactic Survey (JADES). Unless situated in sufficiently (re)ionised regions, Lyman-α emission from these galaxies would be strongly absorbed by neutral gas in the intergalactic medium (IGM). We conservatively estimate sizes of the ionised regions required to reconcile the relatively low Lyman-α velocity offsets (ΔvLyα<300kms−1) with moderately high Lyman-α escape fractions (fesc,Lyα>5%) observed in our sample of LAEs, indicating the presence of ionised ``bubbles'' with physical sizes of the order of 0.1pMpc≲Rion≲1pMpc in a patchy reionisation scenario where the bubbles are embedded in a fully neutral IGM. Around half of the LAEs in our sample are found to coincide with large-scale galaxy overdensities seen in FRESCO at z∼5.8-5.9 and z∼7.3, suggesting Lyman-α transmission is strongly enhanced in such overdense regions, and underlining the importance of LAEs as tracers of the first large-scale ionised bubbles. Considering only spectroscopically confirmed galaxies, we find our sample of UV-faint LAEs (MUV≳−20mag) and their direct neighbours are generally not able to produce the required ionised regions based on the Lyman-α transmission properties, suggesting lower-luminosity sources likely play an important role in carving out these bubbles. These observations demonstrate the combined power of JWST multi-object and slitless spectroscopy in acquiring a unique view of the early stages of Cosmic Reionisation via the most distant LAEs."""
            Relevant: No

            Query: {query}
            Document: """{document}"""
            Relevant:
            '''
        response = openai.chat.completions.create(
            model="text-embedding-ada-002",
            message=prompt.format(query=query, document=document),
            temperature=0,
            logprobs=True,
            logit_bias={7566: 1, 2360: 1},
        )

        return (
            query,
            document,
            response.choices[0].message.content,
            response.choices[0].logprobs.token_logprobs[0],
        )
    
    def get_relevance_for_all_documents(self, result_list, query):
        output_list = []
        for document in result_list:
            try:
                output_list.append(self.document_relevance(query, document=document))
            except Exception as e:
                print(e)
    



    '''
    def __init__(self, retriever=0, collection=0):

        #self.retriever = retriever
        #self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        #self.collection=collection
        load_dotenv()
        os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AOI_KEY")
        self.client=openai.OpenAI()
        self.tokens = [" Yes", " No"]
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.ids = [self.tokenizer.encode(token) for token in self.tokens]
        st.write(self.ids[0])
        st.write(self.ids[1])
    '''
    def get_ids(self):
        st.write(self.ids[0])
        st.write(self.ids[1])


    def get_relevant_documents(self, query, **kwargs):
        results = self.get_documents_by_semantic_search(query)
        return [doc for doc in results if doc['title'].startswith(self.title)]
    
    def get_documents_by_semantic_search(self, text_query):
        semantic_result=self.collection.query(
            query_texts=text_query,
            n_results=15,
            include=['documents']
        )
        # list of document
        return semantic_result

    '''
    async def aget_relevant_documents(self, query, **kwargs):
        results = await self.retriever.aget_relevant_documents(query, **kwargs)
        return [doc for doc in results if doc['title'].startswith(self.title)]
    '''