from fastapi import Request
from ..pipeline.batcher import Batcher

def get_model(request: Request):
    return request.app.state.model

def get_batcher(request: Request) -> Batcher:
    return request.app.state.batcher
