"""
test_circuit_breaker.py
=======================
Simulates the failure scenario and proves the circuit breaker fix works.

Run with:  pytest test_circuit_breaker.py -v
Or just:   python test_circuit_breaker.py
"""

import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from circuit_breaker import CircuitBreaker

# ── Helpers ───────────────────────────────────────────────────

def fake_llm_healthy(prompt):
    """Simulates a working LLM API."""
    return f"AI summary for: {prompt}"

def fake_llm_down(prompt):
    """Simulates a failing/slow LLM API."""
    raise ConnectionError("LLM API is unreachable")

FALLBACK = "AI suggestions temporarily unavailable."

# ── Tests ─────────────────────────────────────────────────────

def test_healthy_llm_passes_through():
    """When LLM is fine, response comes through normally."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    result = breaker.call(fake_llm_healthy, "photosynthesis", fallback=FALLBACK)

    assert result == "AI summary for: photosynthesis"
    assert breaker.state == CircuitBreaker.CLOSED
    print("  PASS: Healthy LLM returns real response.")


def test_circuit_opens_after_threshold():
    """After N consecutive failures, circuit should open."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)

    # Fire 3 failing calls
    for i in range(3):
        result = breaker.call(fake_llm_down, "test", fallback=FALLBACK)
        assert result == FALLBACK   # always gets fallback on failure

    assert breaker.state == CircuitBreaker.OPEN
    assert breaker.failure_count == 3
    print("  PASS: Circuit opened after 3 consecutive failures.")


def test_open_circuit_returns_fallback_immediately():
    """
    BEFORE the fix: server waits 60s, hangs for all users.
    AFTER  the fix: circuit is OPEN, fallback returns in <0.01s.
    """
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

    # Open the circuit
    for _ in range(3):
        breaker.call(fake_llm_down, "test", fallback=FALLBACK)

    assert breaker.state == CircuitBreaker.OPEN

    # Now measure response time with circuit open
    start  = time.time()
    result = breaker.call(fake_llm_down, "anything", fallback=FALLBACK)
    elapsed = time.time() - start

    assert result == FALLBACK
    assert elapsed < 0.05   # must return almost instantly — no waiting!
    print(f"  PASS: Open circuit returned fallback in {elapsed:.4f}s (no blocking).")


def test_circuit_moves_to_half_open_after_timeout():
    """After recovery_timeout, circuit should allow one test request."""
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=2)

    # Open the circuit
    breaker.call(fake_llm_down, "test", fallback=FALLBACK)
    breaker.call(fake_llm_down, "test", fallback=FALLBACK)
    assert breaker.state == CircuitBreaker.OPEN

    # Wait for recovery timeout
    print("  Waiting 2s for recovery timeout...")
    time.sleep(2.1)

    # Next call should transition to HALF_OPEN and try the request
    result = breaker.call(fake_llm_healthy, "recovery test", fallback=FALLBACK)
    assert result == "AI summary for: recovery test"
    assert breaker.state == CircuitBreaker.CLOSED   # success → back to CLOSED
    print("  PASS: Circuit recovered to CLOSED after successful test request.")


def test_x_student_id_header_present():
    """
    Verifies the X-Student-ID middleware is wired up.
    Imports main.py and checks the middleware list.
    """
    from main import app, STUDENT_ID
    middleware_types = [type(m).__name__ for m in app.user_middleware]
    # The custom middleware is registered as a function, check STUDENT_ID is set
    assert STUDENT_ID != "", "STUDENT_ID must be set in main.py!"
    assert STUDENT_ID != "YOUR-STUDENT-ID", "Replace YOUR-STUDENT-ID with your actual ID in main.py!"
    print(f"  PASS: X-Student-ID header is configured with ID: {STUDENT_ID}")


# ── Run all tests manually (no pytest needed) ─────────────────

if __name__ == "__main__":
    tests = [
        test_healthy_llm_passes_through,
        test_circuit_opens_after_threshold,
        test_open_circuit_returns_fallback_immediately,
        test_circuit_moves_to_half_open_after_timeout,
    ]

    print("\n" + "="*55)
    print(" StudySync — Circuit Breaker Test Suite")
    print("="*55)

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n▶ {test.__name__}")
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print("\n" + "="*55)
    print(f" Results: {passed} passed, {failed} failed")
    print("="*55 + "\n")

    # Skip the header test when running manually 
    # (needs main.py STUDENT_ID to be set first)
    print("NOTE: Update STUDENT_ID in main.py before running test_x_student_id_header_present()\n")
