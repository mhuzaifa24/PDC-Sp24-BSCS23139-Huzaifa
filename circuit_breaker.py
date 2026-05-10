import time

class CircuitBreaker:
  
    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 10):
        self.failure_threshold = failure_threshold   
        self.recovery_timeout  = recovery_timeout    
        self.state             = self.CLOSED
        self.failure_count     = 0
        self.last_failure_time = None

    def call(self, func, *args, fallback=None, **kwargs):


        if self.state == self.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                print(f"[CircuitBreaker] Timeout passed. Moving to HALF_OPEN.")
                self.state = self.HALF_OPEN
            else:
                remaining = int(self.recovery_timeout - elapsed)
                print(f"[CircuitBreaker] OPEN. Returning fallback. Retry in {remaining}s.")
                return fallback


        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            print(f"[CircuitBreaker] Call failed: {e}")
            return fallback

    def _on_success(self):
        if self.state == self.HALF_OPEN:
            print("[CircuitBreaker] Test request succeeded. Closing circuit.")
        self.state         = self.CLOSED
        self.failure_count = 0

    def _on_failure(self):
        self.failure_count    += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            if self.state != self.OPEN:
                print(f"[CircuitBreaker] {self.failure_count} failures hit. Opening circuit.")
            self.state = self.OPEN
        else:
            remaining = self.failure_threshold - self.failure_count
            print(f"[CircuitBreaker] Failure {self.failure_count}/{self.failure_threshold}. {remaining} more before OPEN.")


    def get_status(self):
        return {
            "state":          self.state,
            "failure_count":  self.failure_count,
            "failure_threshold": self.failure_threshold,
        }
