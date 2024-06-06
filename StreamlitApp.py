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

llm = ChatOpenAI(temperature=0, model_name= "gpt-3.5-turbo")
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
template= "You are a helpful assistant. Answer all question tp best of your ability"
# Now we can override it and set it to "Friend"
# from langchain_core.prompts.prompt import PromptTemplate

prompt =    ChatPromptTemplate.from_messages( [
        (
            "system",
            template
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)
### Lets Create Chain
chain= prompt | llm

### Chat message history
## Function that stores chat based on session id
store= {}
## Get session history would give you the chat history of the session or it will store it if it is new
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id]= ChatMessageHistory()
    return store[session_id]

with_message_history= RunnableWithMessageHistory(
    chain, get_session_history,
       
)
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
                response= with_message_history.invoke(
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
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat messages from history on app rerun
if len(st.session_state.messages) >2:
    st.text("Chat-history")
    
    for message in st.session_state.messages[:-2]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])