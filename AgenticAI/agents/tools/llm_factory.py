from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from config.settings import settings


class LLMFactory:

    @staticmethod
    def behavioral_llm():

        if settings.LLM_PROVIDER == "groq":
            return ChatGroq(model="llama3-70b-8192", temperature=0)

        return ChatOllama(model="llama3")

    @staticmethod
    def reasoning_llm():

        if settings.LLM_PROVIDER == "groq":
            return ChatGroq(model="deepseek-r1-distill-llama-70b")

        return ChatOllama(model="deepseek-r1")

    @staticmethod
    def graph_llm():

        if settings.LLM_PROVIDER == "groq":
            return ChatGroq(model="deepseek-r1-distill-llama-70b")

        return ChatOllama(model="deepseek-r1")
