from fastapi import FastAPI
from controllers.mawaqitController import router as mawaqitRouter

def create_app() -> FastAPI:
    app = FastAPI(title='Mawaqit Api', debug=False, read_root="/")
    return app

app = create_app()
app.include_router(router=mawaqitRouter)