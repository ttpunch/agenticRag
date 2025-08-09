import requests
from config.settings import LLM_COMPLETION_PATH

def supervisor_agent(state):
    user_query = state["query"]
    prompt = f"""
    Decide if the following query is a RAG search or a Postgres DB query.
    Respond only with 'rag' or 'db'.
    Query: {user_query}
    """
    response = requests.post(LLM_COMPLETION_PATH, json={
        "prompt": prompt,
        "max_tokens": 10,
        "temperature": 0
    }).json()

    task = response["choices"][0]["text"].strip().lower()
    return {**state, "task": task}
