import streamlit as st
import openai
from dotenv import load_dotenv
import os

class costEsimator:

    def __init__(self):
        os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AOI_KEY")
        openai.api_key = os.getenv("OPEN_AOI_KEY")
        # Define the models and their cost per token
        self.cost_per_token=0.001

    def count_tokens(self,text):
        # Estimate the number of tokens in the text without making an API call
        return len(text.split())
 
    def calculate_cost(self, tokens):
        return tokens * self.cost_per_token
