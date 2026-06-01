import torch
from ..model.loader import load_model
from ..pipeline.batcher import Batcher
from fastapi import FastAPI
from src.app.routes import router

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def _startup():
    app.state.model = load_model()
    app.state.batcher = Batcher(app.state.model, 8, 400)
    return app