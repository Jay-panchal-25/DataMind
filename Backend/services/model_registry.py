from dataclasses import dataclass

from core.settings import settings


@dataclass
class CachedModelBundle:
    target: str
    engine: object
    result: dict


class ModelRegistry:
    def get(self, session_state, target: str):
        cached = session_state.model_cache.get(target)
        if cached:
            return cached
        return None

    def set(self, session_state, target: str, engine, result: dict):
        session_state.model_cache[target] = CachedModelBundle(
            target=target,
            engine=engine,
            result=result,
        )

        while len(session_state.model_cache) > settings.AUTOML_CACHE_SIZE:
            oldest_key = next(iter(session_state.model_cache))
            session_state.model_cache.pop(oldest_key, None)


model_registry = ModelRegistry()
