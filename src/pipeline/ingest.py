import random
from typing import Optional
from fastapi import HTTPException, status
import numpy as np

request_ids = []

class Request:
    def __init__(self, features: dict):
        self.features = features
        if "request_id" in features.keys():
            self.request_id = features["request_id"]
        else:
            val = random.randint(10, 999999)
            while val in request_ids:
                val = random.randint(10, 999999)
            self.request_id = val
        self.run_config: Optional[RunConfig] = features["run_config"] if "run_config" in features.keys() else None
        self.validate_schema(features)

        # self.patient_weight: int = features["patient_weight"]
        # self.fibroid_present: bool = features["fibroid_present"]
        # self.num_fibroids: int = features["num_fibroids"]
        # self.fibroid_volume_ratio: float = features["fibroid_volume_ratio"]
        # self.ferritin_proxy: float = features["ferritin_proxy"]
        # self.cycle_length_days: int = features["cycle_length_days"]
        # self.flow_intensity: str = features["flow_intensity"]
        # self.symptom_duration_months: int = int(features["symptom_duration_months"])
        # self.pain_level: int = features["pain_level"]
        # self.age_group: str = features["age_group"]
        # self.prior_pregnancy: bool = features["prior_pregnancy"]
        # self.treatment_type_hormonal: bool = features["treatment_type_hormonal"]
        # self.treatment_type_none: bool = features["treatment_type_none"]
        # self.treatment_type_surgery: bool = features["treatment_type_surgery"]
        # self.ethnicity_Asian: bool = features["ethnicity_Asian"]
        # self.ethnicity_Black: bool = features["ethnicity_Black"]
        # self.ethnicity_Hispanic: bool = features["ethnicity_Hispanic"]
        # self.ethnicity_Other: bool = features["ethnicity_Other"]
        # self.ethnicity_White: bool = features["ethnicity_White"]

    def validate_schema(self, features: dict):
        required_fields = ["patient_weight", "fibroid_present", "cycle_length_days", "symptom_duration_months", "pain_level", "age_group", "prior_pregnancy", 
        "treatment_type_hormonal", "treatment_type_none", "treatment_type_surgery", "ethnicity_Asian", "ethnicity_Black", "ethnicity_Hispanic", 
        "ethnicity_Other", "ethnicity_White"]
        for field in required_fields:
            if features[field] is None or (isinstance(features[field], (float, int)) and np.isnan(features[field])):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"%s is required and cannot be None or NaN" % field
                )

class RunConfig:
    missing_rate: float = 0.0
    seed: Optional[int] = None

def ingest(features: dict):
    req = Request(features)
    return req