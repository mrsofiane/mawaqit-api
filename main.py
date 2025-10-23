import os
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from controllers.mawaqitController import router as mawaqitRouter
from dotenv import load_dotenv

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title='Mawaqit Api', debug=False, read_root="/")

    if os.getenv('USE_REDIS', 'False').lower() == 'true':
        storage_uri = os.getenv('REDIS_URI', 'redis://localhost:6379')
        limiter = Limiter(key_func=get_remote_address, default_limits=[os.getenv("RATE_LIMIT", "60/minute")], storage_uri=storage_uri)
    else:
        limiter = Limiter(key_func=get_remote_address, default_limits=[os.getenv("RATE_LIMIT", "60/minute")])
        
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    return app

app = create_app()
app.include_router(router=mawaqitRouter)