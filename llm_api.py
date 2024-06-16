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

### Api packages
from fastapi import FastAPI
import uvicorn
import nest_asyncio
app= FastAPI()
##Load API keys
load_dotenv()
##Creating title for application

llm = ChatOpenAI(temperature=0, model_name= "gpt-3.5-turbo")
'''
Defining prompt Template dynamically from file.
We can deifne how many ever certificates with input parameters without modifying the code.
'''
    
import yaml
from pprint import pprint
def load_yaml_config(file_path):
    with open(file_path, 'r') as yaml_in:
        yaml_config_list= list(yaml.load_all(yaml_in, Loader= yaml.SafeLoader))
        return yaml_config_list
file_path= "letter_configuration.yaml"
list_of_cert= load_yaml_config(file_path)
prompt_string=""
for cert in list_of_cert:
    #print(cert)
    ## Certificate Details
    cert_name= cert['Name']
    ## Certificate Description
    cert_descr= cert['Description']
    ## Certificate inputs
    param_count=1
    input_param_string=""
    for input_params in cert['input_parameters']:
        input_param_string+= f"{param_count}. {input_params}:\n"
        param_count+=1
    prompt_string+= f"{cert_name}:\n{cert_descr}:\n{input_param_string}\n"
        


## Define LLLM congifuration
template = f"""
You are creating a Certificate for an employee. Please provide the following details:

{prompt_string}

If all the necessary values are provided then summarize the inputs and ask for confirmation.
If user confirms with a confirmation message then convert the details in url format with prefix https://certificates/certificate name/certificate details seperated by '/'.

If you have any questions or need clarification, feel free to ask!

"""

# template= "You are a helpful assistant. Answer all question tp best of your ability"
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

##Create basic chain from prompt
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

## Model chain with Message history
with_message_history= RunnableWithMessageHistory(
    chain, get_session_history,
    
)

## Create session id configuration
config= {"configurable": {"session_id":"vikas"}}


###########################################
## API Calling
static_string=" Initial text"
@app.post("/query")
async def add_text(question: str):
    global static_string
    static_string +=question
###########################################

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
          

    else:
        
        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion tokens: {cb.completion_tokens}")
        print(f"Total Cost:{cb.total_cost}")
        
        #print(response.content)
        if isinstance(response.content, str):
            return {"message": "Text added", "current_string": response.content}
        else:
            return {"message": "Text added", "current_string": "no answer"}



if __name__ == "__main__":
    nest_asyncio.apply()
    uvicorn.run(app)