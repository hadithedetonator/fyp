# File: llm.py
from langchain_community.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
MODEL="/home/hadi/TutorAI-FYP/fyp/app/models/llama-2-7b-chat.Q3_K_M.gguf"

# Instantiate the callback with a streaming stdout handler
cb =   CallbackManager([StreamingStdOutCallbackHandler()])   

# Loading the Llama 2's LLM
def load_llm():
    # A Llama 2 based LLM model 
    llm:LlamaCpp  = LlamaCpp(
        model_path=MODEL,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        callback_manager=cb, 
        verbose=True,
        n_ctx=2000
    )
    return llm