from functools import wraps
from ..memory.provider import MemoryProvider



def with_memory(provider: callable=MemoryProvider):
    """
    Decorator to inject a fresh Redis MemoryRootCluster instance into an Aiogram handler.

    The handler will receive `root` as a keyword argument. If `root` is already provided
    in `kwargs`, it will not be overwritten.

    Returns:
        callable: The decorated handler with Redis MemoryRootCluster injection.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapped_handler(event, *args, **kwargs):
            if 'memory' not in kwargs:
                kwargs['memory'] = provider()

            try:
                return await handler(event, *args, **kwargs)
            finally:
                # Help GC in long-lived workers
                del kwargs['memory']
        return wrapped_handler
    return decorator
