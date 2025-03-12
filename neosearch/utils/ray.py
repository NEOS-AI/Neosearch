import ray

# custom modules
from neosearch.constants.queue import USE_QUEUE


# decorator for ray remote
def ray_remote_if_enabled(func):
    if not USE_QUEUE:
        return ray.remote(func)
    return func
