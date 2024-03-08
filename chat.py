from streamlit_chat import message
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

class Chat:

    def __init__(self, database):
        if 'history' not in st.session_state:
            st.session_state['history'] = []
        if 'generated' not in st.session_state:
            st.session_state['generated'] = ["Ciao! Ho alcune risposte (forse)"]
        if 'past' not in st.session_state:
            st.session_state['past'] = ["Ciao! Ho alcune domande"]
        # Create containers for chat history and user input
        self.response_container = st.container()
        self.container = st.container()
        
        #create covnersational chain
        self.__chain = self.__get_conversational_chain(database)

    def __get_conversational_chain(self, database):
        st.session_state.conversation=database
        llm = ChatOpenAI()
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=database.as_retriever(search_kwargs={"k": 5}),
        )
        return conversation_chain

    def __conversational_chat(self, query, chain):
        result = chain({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        return result["answer"]

    def chat(self):
        # User input form
        with self.container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Question:", placeholder="Chiedi quello che vuoi ai documenti APRA", key='input')
                submit_button = st.form_submit_button(label='Send')
            if submit_button and user_input:
                output = self.__conversational_chat(user_input, self.__chain)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        # Display chat history
        if st.session_state['generated']:
            with self.response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', logo=('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT5NyDxIkmwUsJeq3W3hEKBGagV5su6CE1sZQ&usqp=CAU'))
                    message(st.session_state["generated"][i], key=str(i), logo=('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYzs4aNNoy8aM6p0cArrghtTo4MqOaDk5otpXuGXN1eIxpT3EHhTyLvel0c-bx15oKb1o&usqp=CAU'))

                    #st.write(user_template.replace(
                    #"{{MSG}}", st.session_state["past"][i]), unsafe_allow_html=True)
                    #st.write(bot_template.replace(
                    #"{{MSG}}", st.session_state["generated"][i]), unsafe_allow_html=True)
                    #message(st.session_state["generated"][i], key=str(i), avatar_style=f"custom-avatar")