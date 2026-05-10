## BSCS23139     -    Muhammad Huzaifa Saleem



## Assignment: Building Resilient Distributed Systems
**Problem Implemented:** Circuit Breaker Pattern (Problem 3 — LLM Fault Tolerance)

#### Video Link: https://drive.google.com/file/d/18SHT68nGy3y0P_sQzavSr3ZbQPMQZNDB/view?usp=sharing
---

## Project Structure

```
studysync/
├── main.py                  # FastAPI app + X-Student-ID middleware + endpoints
├── circuit_breaker.py       # Circuit breaker logic (CLOSED / OPEN / HALF_OPEN)
├── llm_service.py           # Mocked LLM API (toggle up/down to simulate failure)
├── test_circuit_breaker.py  # Test suite — proves failure + fix
└── README.md
```

---

## How to Run

### 1. Install dependencies
```bash
pip install fastapi uvicorn httpx pytest
```

### 3. Start the server
```bash
uvicorn main:app --reload
```
Server runs at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

---

## How to Demo (for the video)

### Step 1 — Show the bug (WITHOUT the fix)
Open `llm_service.py` and set `LLM_IS_DOWN = True`.  
Call `/ai/summarize` and watch the server hang for seconds — every request blocks.

### Step 2 — Show the fix (WITH the circuit breaker)
Use the API endpoints to simulate failure dynamically:

```bash
# 1. Bring the LLM down
curl -X POST http://localhost:8000/simulate/llm-down

# 2. Call summarize 3 times — watch circuit open
curl -X POST "http://localhost:8000/ai/summarize?prompt=photosynthesis"
curl -X POST "http://localhost:8000/ai/summarize?prompt=photosynthesis"
curl -X POST "http://localhost:8000/ai/summarize?prompt=photosynthesis"

# 3. Circuit is now OPEN — this returns instantly with fallback
curl -X POST "http://localhost:8000/ai/summarize?prompt=photosynthesis"

# 4. Check circuit state
curl http://localhost:8000/health

# 5. Bring LLM back up
curl -X POST http://localhost:8000/simulate/llm-up

# 6. Reset breaker and verify recovery
curl -X POST http://localhost:8000/simulate/reset-breaker
curl -X POST "http://localhost:8000/ai/summarize?prompt=photosynthesis"
```

## How to Run Tests

```bash
# Run with pytest
pytest test_circuit_breaker.py -v

# Or run directly
python test_circuit_breaker.py
```

---

## What the Tests Prove

| Test | What it shows |
|------|--------------|
| `test_healthy_llm_passes_through` | Normal flow works fine |
| `test_circuit_opens_after_threshold` | Circuit opens after 3 failures |
| `test_open_circuit_returns_fallback_immediately` | **No blocking** — fallback in <0.05s |
| `test_circuit_moves_to_half_open_after_timeout` | Auto-recovery after timeout |
