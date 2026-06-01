from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from ..metrics.timer import timer
from ..pipeline.ingest import ingest
from ..pipeline.preprocess import preprocess
from ..pipeline.inference import inference
from ..pipeline.decision import decision
from ..utils.logging import Counters, log_request
from .dependencies import get_batcher, get_model

router = APIRouter()
counters = Counters()

_PREDICT_UI_PATH = Path(__file__).resolve().parent / "static" / "predict.html"


@router.get("/")
def read_root():
    return {"message": "Hello, World! go to /input to submit a request and see the result at /predict. check /docs for the OpenAPI spec and /health for the health check."}

@router.get("/input", response_class=HTMLResponse)
def predict_form():
    return HTMLResponse(_PREDICT_UI_PATH.read_text(encoding="utf-8"))

@router.post("/predict")
async def predict(request: Request, model=Depends(get_model), batcher=Depends(get_batcher)):
    timings = {}
    req = None
    dec = None
    try:
        body = await request.json()
        with timer() as t:
            print(body)
            # body["run_config"] = {"missing_rate": 0.2, "seed": 32}
            req = ingest(body)
            ingest_ms = t.ms
            features = preprocess(req)
            preprocess_ms = t.ms - ingest_ms
        #     pred = await batcher.add(features)
            score = inference(features, model)
            inference_ms = t.ms - preprocess_ms
            dec = decision(req.request_id, score, features.missing_rate)
            decision_ms = t.ms - inference_ms
            print("all done")
            total_ms = t.ms
        timings = {"ingest": ingest_ms, "preprocess": preprocess_ms, "inference": inference_ms, "decision": decision_ms, "total": total_ms}
        log_request(request_id=str(req.request_id), timings_ms=timings, counters=counters, status="success", decision=dec)
        return {"decision": dec, "timing_ms:": timings}
    except Exception as e:
        request_id = str(req.request_id) if req is not None else None
        log_request(request_id=request_id, timings_ms=timings, counters=counters, status="failure", decision=dec, error=str(e), error_type=type(e).__name__)
        raise

@router.get("/health")
def health_check():
    return {"status": "ok"}