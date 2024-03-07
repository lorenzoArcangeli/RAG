
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.chains import LLMChain

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPEN_AOI_KEY")


# Few Shot Examples
examples = [
    {
        "input": "I membri della Polizia potrebbero eseguire arresti?",
       "output": "Cosa possono fare i membri della polizia?",
    },
    {
        "input": "In che stato è nato Jan Sindel?",
        "output": "Quale è la storia personale di Jan Sindel?",
    },
]
# We now transform these to example messages
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Sei un esperto di conoscenza del mondo. Il tuo compito è quello di fare un step-back e parafrasare 
            una domanda a una domanda più generica, che è più facile da rispondere
            NOTA IMPORTANTE: se è una domanda è completamente priva di contesto restituisci la domanda originale che
            ti è statata fonita senza aggiungere altro e senza aggiungere nessun commento.
            Ecco alcuni esempi:""",
        ),
        # Few shot examples
        few_shot_prompt,
        # New question
        ("user", "{question}"),
    ]
)

question_gen = prompt | ChatOpenAI(temperature=0) | StrOutputParser()

llm = ChatOpenAI(
        temperature=0,
        max_tokens=800,
        model_kwargs={"top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
    )

def query_expansion(query):
    QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""Sei un AI language model assistant. Il tuo compito è quello di generare tre
            diverse versioni della domanda data dall'utente per recuperare i documenti pertinenti da un
            database vettoriale. Generando più prospettive sulla domanda dell'utente, il vostro obiettivo è quello di aiutare
            l'utente a superare alcune delle limitazioni della ricerca of the distance-based similarity
            Fornisce queste domande alternative separate da newlines. Fornisce solo la query, nessuna numerazione.Insersci nella prima riga la query originale che ricevi in input
            (solo la domanda originale, niente altro) senza separazione con la riga sottostante.
            NON aggiungere la doppia interruzione di riga. 
            Il template dell'output deve essere il seguente:
            query 1
            query 2
            query 3
            query 4
            Domanda originale: {question}""",
        )

    llm_chain = LLMChain(llm=llm, prompt=QUERY_PROMPT)
    queries = llm_chain.invoke(query)
    queries = queries.get("text")
    queries_splitted = queries.split("\n")
    return queries_splitted

def join_query_transofrmed(query_list):
    return "|-|".join(query_list)