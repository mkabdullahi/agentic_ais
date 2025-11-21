# Minimal LLM call wrapper with retries and method fallbacks
import time
import logging

logger = logging.getLogger(__name__)

def call_llm_with_retries(llm, *args, retries=3, backoff=1.5, **kwargs):
    last_exc = None
    for attempt in range(1, retries + 1):
        for method in ("generate", "chat", "__call__", "request"):
            fn = getattr(llm, method, None)
            if not callable(fn):
                continue
            try:
                resp = fn(*args, **kwargs)
            except Exception as e:
                last_exc = e
                logger.debug("LLM method %s raised: %s", method, e)
                continue
            if resp:
                return resp
            logger.debug("LLM method %s returned empty on attempt %d", method, attempt)
        time.sleep(backoff * attempt)
    raise RuntimeError(f"LLM returned empty response after {retries} attempts. Last error: {last_exc}")