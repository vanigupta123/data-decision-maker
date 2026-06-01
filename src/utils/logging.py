from datetime import datetime, timezone
import json
import sys
from typing import Any, Dict, Optional
from dataclasses import asdict, is_dataclass

class Counters:
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    abstain_count: int = 0


def log_request(request_id: str,
    timings_ms: Dict[str, float],
    counters: Counters,
    status: str,  # "success" or "failure"
    decision: Optional[Any] = None,
    error: Optional[str] = None,
    error_type: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    counters.total_requests += 1
    if status == "success":
        counters.success_count += 1
    else:
        counters.failure_count += 1
    
    decision_dict: Optional[Dict[str, Any]] = None
    if decision is not None:
        if is_dataclass(decision):
            decision_dict = asdict(decision)
        elif isinstance(decision, dict):
            decision_dict = decision
        else:
            try:
                decision_dict = {
                    k: v for k, v in vars(decision).items() if not k.startswith("_")
                }
            except TypeError as exc:
                raise ValueError("decision isn't formatted properly") from exc
        
        if decision_dict.get("abstained") is True:
            counters.abstain_count += 1
        
    event: Dict[str, Any] = {
        "event": "predict_request",
        "request_id": request_id,
        "status": status,
        "timings_ms": timings_ms,
        "decision": decision_dict,
        "error": error,
        "error_type": error_type,
        "counters": {
            "total": counters.total_requests,
            "success": counters.success_count,
            "failure": counters.failure_count,
            "abstained": counters.abstain_count,
        },
    }

    if extra:
        event["extra"] = extra
    log_event(event)

def log_event(event: Dict[str, Any]):
    event = dict(event) 
    event.setdefault("ts", datetime.now(timezone.utc).isoformat())
    sys.stdout.write(json.dumps(event, separators=(",", ":"), default=str) + "\n")
    sys.stdout.flush()
    