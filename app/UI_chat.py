from streamlit_chat import message
import streamlit as st
from langchain_openai import ChatOpenAI 
#from langchain.chat_models import ChatOpenAI # questo è deprecato
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain


class UIChat:

    def __init__(self, database):
        #is used to store question/answers to display
        if "history" not in st.session_state:
            st.session_state['history'] = []
            st.session_state['history'].append({"role": "assistant", "content": "Ciao! Sono l'assistente virtuale di Essenzia. Chiedimi qualcosa"})
        #is used to store chat history for the LLM since dict is not allowed
        if "chat_history" not in st.session_state:
            st.session_state['chat_history'] = []
        
        self.__chain = self.__get_conversational_chain(database)
        
    def __get_conversational_chain(self, database):
        '''
        st.session_state.conversation=database
        template = """
        Sei l'assistente virtuale di un azienda inforamtica. Prendendo in considerazione il contesto fornito e la chat history devi rispondere
        alla domanda dell'utente. Se non hai la risposta non inventarti niente. Rispondi dicendo che non sai la risposta ma cerca di dare un
        riassunto del contesto preso in input.
        
        CONTEXT:
        {context}
        
        QUESTION: 
        {query}

        CHAT HISTORY: 
        {chat_history}
        
        ANSWER:
        """

        prompt = PromptTemplate(input_variables=["chat_history", "query", "context"], template=template)
        memory = ConversationBufferMemory(memory_key="chat_history", input_key="query")

        chain = RetrievalQA.from_chain_type(ChatOpenAI(model="gpt-3.5-turbo", temperature=0), chain_type="stuff", memory=memory, prompt=prompt)
        '''
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=database.as_retriever(search_kwargs={"k": 5}),
        )
        return conversation_chain
        #return chain

    def __conversational_chat(self, query, chain):
        result = chain({"question": query, "chat_history": st.session_state['chat_history']})
        #LLM chat history
        st.session_state['chat_history'].append((query, result["answer"]))
        return result["answer"]

    def chat(self):
        # markdown style for text
        st.markdown(
            """
            <style>
                body {
                    background-color: #212121;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        #sidebar
        with st.sidebar:
            st.title('🤖💬 APRA Chatbot')
            st.write("Benvenuto nel nostro assistente virtuale! Sono qui per rispondere alle tue domande, risolvere problemi e offrirti supporto tecnico personalizzato. Digita semplicemente la tua richiesta e sarò felice di aiutarti nel miglior modo possibile.")

        #chat
        for message in st.session_state['history']:
            role = message["role"]
            if role == "user":
                with st.chat_message('user', avatar="https://cdn-icons-png.flaticon.com/512/5987/5987424.png"):
                    st.markdown(message['content'], unsafe_allow_html=True)
            else:
                with st.chat_message('assistant', avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYzs4aNNoy8aM6p0cArrghtTo4MqOaDk5otpXuGXN1eIxpT3EHhTyLvel0c-bx15oKb1o&usqp=CAU"):
                    st.markdown(message['content'], unsafe_allow_html=True)

        if prompt := st.chat_input("Domanda: "):
            st.session_state['history'].append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="https://cdn-icons-png.flaticon.com/512/5987/5987424.png"):
                st.markdown(prompt, unsafe_allow_html=True)
            with st.chat_message("assistant", avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYzs4aNNoy8aM6p0cArrghtTo4MqOaDk5otpXuGXN1eIxpT3EHhTyLvel0c-bx15oKb1o&usqp=CAU"):
                message_placeholder = st.empty()
                full_response = ""
                full_response= self.__conversational_chat(prompt, self.__chain)
                message_placeholder.markdown(full_response, unsafe_allow_html=True)
            st.session_state['history'].append({"role": "assistant", "content": full_response})
