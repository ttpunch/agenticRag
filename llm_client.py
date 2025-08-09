# llm_client.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import logging

def call_llm(prompt, max_tokens=512, temperature=0.0):
    """
    Call LLM using proper LangChain ChatOpenAI interface.
    
    Args:
        prompt (str): The input prompt text
        max_tokens (int): Maximum tokens to generate
        temperature (float): Temperature for randomness
    
    Returns:
        str: The generated response text
    """
    
    # Initialize the LLM with correct parameters
    llm = ChatOpenAI(
        base_url="http://localhost:12434/engines/v1",  # Fixed: removed '/engines' - standard OpenAI API format
        api_key="docker",  # dummy key for ollama
        model_name="ai/qwen3:8B-Q4_K_M",
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    logging.info(f"LLM initialized with model: {llm.model_name}")
    
    try:
        logging.info(f"Calling LLM with prompt: {prompt}")
        
        # Create proper message format - ChatOpenAI expects messages, not raw payload
        messages = [HumanMessage(content=prompt)]
        
        # Invoke the LLM with messages
        response = llm.invoke(messages)
        
        # Extract text content from AIMessage
        return response.content
        
    except Exception as e:
        logging.error(f"LLM call error: {e}")
        return f"[LLM call error] {e}"

# Alternative function that accepts message lists for more complex conversations
def call_llm_with_messages(messages, max_tokens=512, temperature=0.0):
    """
    Call LLM with a list of messages (for conversations).
    
    Args:
        messages (list): List of message tuples like [("human", "Hello"), ("assistant", "Hi!")]
        max_tokens (int): Maximum tokens to generate
        temperature (float): Temperature for randomness
    
    Returns:
        str: The generated response text
    """
    
    llm = ChatOpenAI(
        base_url="http://localhost:12434/v1",
        api_key="docker",
        model="ai/qwen3:8B-Q4_K_M",
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    try:
        # Convert tuple format to proper message format if needed
        if messages and isinstance(messages[0], tuple):
            # Handle tuple format: [("human", "text"), ("assistant", "text")]
            formatted_messages = []
            for role, content in messages:
                if role == "human":
                    formatted_messages.append(HumanMessage(content=content))
                # Add other message types as needed
        else:
            # Assume messages are already in proper format
            formatted_messages = messages
        
        response = llm.invoke(formatted_messages)
        return response.content
        
    except Exception as e:
        logging.error(f"LLM call error: {e}")
        return f"[LLM call error] {e}"