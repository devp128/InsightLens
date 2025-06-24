from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

prompt = PromptTemplate(
    input_variables=["query"],
    template="You are a helpful assistant. Echo the user's query: {query}"
)

llm = ChatOpenAI(
    model_name="deepseek/deepseek-r1-0528:free",  
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_API_BASE,
)
echo_chain = LLMChain(llm=llm, prompt=prompt)

def run_echo_chain(query: str) -> str:
    return echo_chain.run(query=query)
