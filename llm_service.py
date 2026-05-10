import time

LLM_IS_DOWN = False

def call_llm_api(prompt: str) -> str:


    if LLM_IS_DOWN:
        print("[LLM Service] API is down! Simulating 5s timeout...")
        time.sleep(5)  
        raise ConnectionError("LLM API is unreachable")


    return f"Here is an the LLM Response fOR : '{prompt}' :- ........"
