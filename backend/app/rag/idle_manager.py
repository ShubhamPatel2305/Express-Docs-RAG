import asyncio
import logging
import time

logger = logging.getLogger(__name__)

# Updated by the chat router on every request
last_request_time: float = time.time()
IDLE_TIMEOUT_SECONDS = 300  # 5 minutes
_monitor_task: asyncio.Task | None = None


def record_request():
    """Call this on every incoming chat request."""
    global last_request_time
    last_request_time = time.time()


def _offload_models():
    """Clear all lru_cache singletons to release RAM."""
    try:
        from app.rag.embeddings import get_embedder
        from app.rag.retriever import get_retriever
        from app.rag.reranker import get_reranker

        get_embedder.cache_clear()
        get_retriever.cache_clear()
        get_reranker.cache_clear()

        # Also explicitly delete the heavy objects so GC can collect immediately
        import gc
        gc.collect()

        logger.info("Idle timeout reached — models offloaded from memory.")
    except Exception as e:
        logger.error(f"Error during model offload: {e}")


async def _idle_monitor():
    """Background task — checks every 60s for inactivity."""
    offloaded = False

    while True:
        await asyncio.sleep(60)
        idle_seconds = time.time() - last_request_time

        if idle_seconds >= IDLE_TIMEOUT_SECONDS and not offloaded:
            logger.info(f"No requests for {idle_seconds:.0f}s — offloading models.")
            _offload_models()
            offloaded = True

        elif idle_seconds < IDLE_TIMEOUT_SECONDS and offloaded:
            # Reset flag when traffic resumes (models reload lazily on next request)
            offloaded = False
            logger.info("Traffic resumed — models will reload on next request.")


def start_idle_monitor():
    global _monitor_task
    loop = asyncio.get_event_loop()
    _monitor_task = loop.create_task(_idle_monitor())
    logger.info(f"Idle monitor started — offload after {IDLE_TIMEOUT_SECONDS}s inactivity.")


def stop_idle_monitor():
    global _monitor_task
    if _monitor_task:
        _monitor_task.cancel()
        _monitor_task = None