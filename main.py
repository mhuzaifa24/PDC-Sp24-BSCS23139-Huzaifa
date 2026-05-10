from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from circuit_breaker import CircuitBreaker
import llm_service


app = FastAPI(title="StudySync API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


STUDENT_ID = "BSCS 23139"   

@app.middleware("http")
async def add_student_id_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Student-ID"] = STUDENT_ID
    return response


breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=30)

FALLBACK_RESPONSE = "AI suggestions are temporarily unavailable. Please try again shortly."



@app.get("/")
def root():
    return {"message": "StudySync API is running."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "circuit_breaker": breaker.get_status()
    }


@app.post("/ai/summarize")
def summarize(prompt: str):
   
    start = time.time()

    result = breaker.call(
        llm_service.call_llm_api,
        prompt,
        fallback=FALLBACK_RESPONSE
    )

    elapsed = round(time.time() - start, 3)

    return {
        "prompt":          prompt,
        "response":        result,
        "circuit_state":   breaker.get_status()["state"],
        "response_time_s": elapsed,
        "used_fallback":   result == FALLBACK_RESPONSE
    }


@app.post("/simulate/llm-down")
def simulate_llm_down():
    """Toggle the LLM to simulate it going down."""
    llm_service.LLM_IS_DOWN = True
    return {"message": "LLM API is now DOWN. Call /ai/summarize to see circuit breaker in action."}


@app.post("/simulate/llm-up")
def simulate_llm_up():
    """Toggle the LLM back to healthy."""
    llm_service.LLM_IS_DOWN = False
    return {"message": "LLM API is now UP again."}


@app.post("/simulate/reset-breaker")
def reset_breaker():
    """Manually reset the circuit breaker to CLOSED."""
    breaker.state         = CircuitBreaker.CLOSED
    breaker.failure_count = 0
    return {"message": "Circuit breaker reset to CLOSED."}
