from typing import List, Dict, Generator
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings

class GenerationService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        
        if self.provider == "groq":
            if not settings.GROQ_API_KEY:
                 # Fallback check
                 key = os.getenv("GROQ_API_KEY")
                 if not key:
                     raise ValueError("GROQ_API_KEY not set.")
            
            # Initialize ChatGroq
            self.llm = ChatGroq(
                temperature=0, 
                model_name=settings.LLM_MODEL, # e.g. llama3-8b-8192
                api_key=settings.GROQ_API_KEY
            )
        else:
            raise NotImplementedError(f"Provider {self.provider} not supported yet.")

        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful and accurate assistant. 
            Answer the question based ONLY on the following context. 
            If the answer is not in the context, say "I don't have enough information to answer that."

            Context:
            {context}

            Question: {question}
            """
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_response(self, query: str, context_chunks: List[Dict]) -> str:
        """
        Generate answer from context.
        """
        # Format context
        # context_chunks is list of dicts with 'text' and 'metadata'
        context_text = "\n\n".join([c.get('text', '') for c in context_chunks])
        
        try:
            response = self.chain.invoke({
                "context": context_text,
                "question": query
            })
            return response
        except Exception as e:
            print(f"Generation error: {e}")
            return "Sorry, I encountered an error generating the response."
            
    def generate_stream(self, query: str, context_chunks: List[Dict]) -> Generator[str, None, None]:
        context_text = "\n\n".join([c.get('text', '') for c in context_chunks])
         
        try:
            for chunk in self.chain.stream({"context": context_text, "question": query}):
                yield chunk
        except Exception as e:
            print(f"Stream error: {e}")
            yield "Error generating response."
