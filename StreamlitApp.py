import os
import traceback
from dotenv import load_dotenv
# from src.policy_bot.policy_details import generate_evaluate_chain
# from src.policy_bot.utils import read_file
import streamlit as st
from langchain.callbacks import get_openai_callback

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI
### Packages which handle Chat history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
##Chat prompt Template
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
##Load API keys
load_dotenv()
if 'llm' not in st.session_state:
    llm = ChatOpenAI(temperature=0, model_name= "gpt-3.5-turbo")
    st.session_state['llm']= llm
if 'template' not in st.session_state:
    ## Define LLLM congifuration
    template = """
    You are creating a Certificate for an employee. Please provide the following details:

    Employment Resignation:
    This certificate generates resignation details of employee. If language is German then Formular id= ARB_AUS else Formular id= ARB_AUS_EN and generates certificate provided below information:
    1. Employee Id: 
    2. Bv Number:
    3. Effective Date (YYYY-MM-DD):
    4. Language (English or German): 

    If all the necessary values are provided then summarize the inputs and ask for confirmation.
    If user confirms with a confirmation message then convert the details in url format with prefix https://certificates/certificate name/certificate details seperated by '/'.


    Employment details:
    This certificate generates employment details of employee requested. If language is German then Formular id= ARB_ESS else Formular id= ARB_ESS_EN and generates certificate provided below information:
    1. Employee Id: 
    2. Bv Number:
    3. Effective Date (YYYY-MM-DD):
    4. Language (English or German): 

    If all the necessary values are provided then summarize the inputs and ask for confirmation.
    If user confirms with a confirmation message then convert the details in url format with prefix https://certificates/certificate name/certificate details seperated by '/'.

    If you have any questions or need clarification, feel free to ask!

    """
    st.session_state['template']= template

# template= "You are a helpful assistant. Answer all question tp best of your ability"
# Now we can override it and set it to "Friend"
# from langchain_core.prompts.prompt import PromptTemplate
if 'prompt' not in st.session_state:
    prompt =    ChatPromptTemplate.from_messages( [
            (
                "system",
                st.session_state.template
            ),
            MessagesPlaceholder(variable_name="messages")
        ]
    )
    st.session_state['prompt']= prompt

##Create basic chain from prompt
if 'chain' not in st.session_state:
    ### Lets Create Chain
    chain= prompt | st.session_state.llm
    st.session_state['chain']= chain

### Chat message history
## Function that stores chat based on session id
if 'store' not in st.session_state:
    store= {}
    st.session_state['store']= store


    ## Get session history would give you the chat history of the session or it will store it if it is new
if 'get_session_history' not in st.session_state:
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in st.session_state.store:
            st.session_state.store[session_id]= ChatMessageHistory()
        return st.session_state.store[session_id]
    st.session_state.get_session_history= get_session_history

## Model chain with Message history
if 'with_message_history' not in st.session_state:
    with_message_history= RunnableWithMessageHistory(
        chain, st.session_state.get_session_history,
        
    )
    st.session_state['with_message_history']= with_message_history

## Create session id configuration
config= {"configurable": {"session_id":"vikas"}}

##Creating title for application
# st.title("Policy bot: A Knowledge bot which provides you answers regarding policies exist in company")
st.header('Certificate Creator', divider='rainbow')
st.subheader('A Bot which will help you create certificates for you')

###########################################

st.title("Chat here...")
messages = st.container(height=200)


if question := st.chat_input("Ask something"):
    messages.chat_message("user").write(question)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    ##messages.chat_message("assistant").write(f"Echo: {prompt}")
    ###########################################
    

    with st.spinner("Fetching details..."):
        try:
            ##Execute evaluate chain
            with get_openai_callback() as cb:
                response= st.session_state.with_message_history.invoke(
                    {
                        "messages": [HumanMessage(content= question)]
                    }, config= config
                )

        except Exception as e:
            traceback.print_exception(type(e),e, e.__traceback__)
            st.error("Error")      
        
        else:
            
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion tokens: {cb.completion_tokens}")
            print(f"Total Cost:{cb.total_cost}")
            
            if isinstance(response, str):
                #answer= response.get("policy_response")
                st.text_area(label= "Reponse", value= response.content)
            else:
                
                messages.chat_message("assistant").write(response.content)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response.content})
with st.sidebar:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Display chat messages from history on app rerun
    if len(st.session_state.messages) >2:
        st.text("Chat-history")
        
        for message in st.session_state.messages[:-2]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])