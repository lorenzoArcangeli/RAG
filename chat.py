from streamlit_chat import message
import streamlit as st
#from langchain_openai import ChatOpenAI 
from langchain.chat_models import ChatOpenAI #questo è deprecato
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.question_answering import load_qa_chain

from langchain import PromptTemplate


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

        '''
        self.memory = ConversationBufferWindowMemory(
            memory_key='chat_history', return_messages=True, 
            k=5)
        '''
        #create covnersational chain
        self.__chain = self.__get_conversational_chain(database)
        #st.session_state.conversation=self.__get_conversational_chain(database)

    def __get_conversational_chain(self, database):
        st.session_state.conversation=database
        llm = ChatOpenAI()
        '''
        #retrieved_documents=database.get_documents_by_semantic_search()
        #st.write("retrieved documents")
        #st.write(retrieved_documents)
        template = """
        If the virtual assistant of a computer company. The main business of the company is within management software. Your task is to respond to the topics provided by the user based on the context and the history of the chat in progress. Most questions will be provided in Italian, so answer in Italian
        
        CONTEXT:
        {context}
        
        QUESTION: 
        {query}

        CHAT HISTORY: 
        {chat_history}
        
        ANSWER:
        """

        prompt = PromptTemplate(input_variables=["chat_history", "query", "context"], template=template)
        #memory = ConversationBufferMemory(memory_key="chat_history", input_key="query")
        conversation_chain = load_qa_chain(ChatOpenAI(temperature=0), chain_type="stuff", prompt=prompt)
        #conversation_chain = load_qa_chain(ChatOpenAI(temperature=0), chain_type="stuff" memory=memory (memory era commentato), prompt=prompt)
        return conversation_chain
        '''
        #system_template="You are the virtual assistant of a computer company. The main business of the company is within management software. Your task is to respond to the topics provided by the user based on the context and the history of the chat in progress. Most questions will be provided in Italian, so answer in Italian"
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            #retriever=database.as_retriever(),
            retriever=database,
            #combine_docs_chain_kwargs={"prompt": prompt}
            #memory=self.memory
        )
        return conversation_chain

    def __conversational_chat(self, query, chain):
        #response = chain({"question": query, "chat_history": st.session_state['history']})
        response = chain({"question": query, "chat_history": st.session_state['history']})
        if len(st.session_state['history'])>=5:
            st.session_state['history'].pop(0)
        st.session_state['history'].append((query, response["answer"]))
        #self.__update_history(st.session_state['history'], query, response['chat_history'])

        #result=chain({"question": query})
        #st.session_state['history']=result['chat_history']


        #result = chain({"question": query, "chat_history": st.session_state['history']})
        #st.session_state['history'].append((query, response["answer"]))

        #response = st.session_state.conversation({'question': query})
        #st.session_state.chat_history = response['chat_history']
        st.write("conversational chain")
        st.write(st.session_state['history'])
        return response["answer"]
    
    def __update_history(self, history, query, answer):
        if len(history)>=1:
            history.pop(0)
        history.append((query, answer))

    def chat(self):

        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None

        # User input form
        with self.container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input("Query:", placeholder="Chiedi quello che vuoi ai documenti APRA", key='input')
                submit_button = st.form_submit_button(label='Send')
            if submit_button and user_input:
                output = self.__conversational_chat(user_input, self.__chain)
                st.session_state['past'].append(user_input)
                st.session_state['generated'].append(output)

        # Display chat history
        if st.session_state['generated']:
            with self.response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', logo=('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqOMGqQLsbFusOzwAIa0J1y5_aGLlZ086ahA&usqp=CAU'))
                    message(st.session_state["generated"][i], key=str(i), logo=('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYzs4aNNoy8aM6p0cArrghtTo4MqOaDk5otpXuGXN1eIxpT3EHhTyLvel0c-bx15oKb1o&usqp=CAU'))

                    #st.write(user_template.replace(
                    #"{{MSG}}", st.session_state["past"][i]), unsafe_allow_html=True)
                    #st.write(bot_template.replace(
                    #"{{MSG}}", st.session_state["generated"][i]), unsafe_allow_html=True)
                    #message(st.session_state["generated"][i], key=str(i), avatar_style=f"custom-avatar")