import os
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from controllers.mawaqitController import router as mawaqitRouter
from config.settings import settings

def create_app() -> FastAPI:
    app = FastAPI(title='Mawaqit Api', debug=False, read_root="/")

    if settings.ENABLE_REDIS:
        storage_uri = settings.REDIS_URI
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT], storage_uri=storage_uri)
    else:
        limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    return app

app = create_app()
app.include_router(router=mawaqitRouter)