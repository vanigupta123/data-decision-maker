import json
import torch
import numpy as np
from fastapi import HTTPException, status
from ..pipeline.ingest import Request
from pathlib import Path

STATS_PATH = Path(__file__).parent.parent / "model" / "artifacts" / "preprocessing_stats.json"
with open(STATS_PATH, 'r') as file:
    DATA = json.load(file)

def preprocess(request: Request):
    feat = Features(request)
    return feat

class Features:
    def __init__(self, request: Request):
        self.request = request
        self.request_id = request.request_id
        self.run_config = request.run_config
        self.features_dictionary, self.missing_rate, self.x = self.transform(request.features)

    # implement all deterministic transformations here
    def transform(self, request: dict):
        # fill missing values with fixed default values
        # normalize fixed constants
        d = dict()
        cols = ["patient_id", "patient_weight", "num_fibroids", "fibroid_volume_ratio", 
        "ferritin_proxy", "cycle_length_days", "flow_intensity", "symptom_duration_months", 
        "pain_level", "age_group_encoded", "prior_pregnancy", "flow_intensity_missing", 
        "treatment_type_hormonal", "treatment_type_none", "treatment_type_surgery", 
        "ethnicity_Asian", "ethnicity_Black", "ethnicity_Hispanic", "ethnicity_Other", "ethnicity_White"]
        d = {k: None for k in cols}        
        d["patient_id"] = self.request_id

        normalize_cols = ["cycle_length_days", "symptom_duration_months", "pain_level", "ferritin_proxy"]
        optional_cols = ["num_fibroids", "fibroid_volume_ratio", "ferritin_proxy", "flow_intensity", "flow_intensity_missing"]
        age_group_mapping = {'18-29': 0, '30-44': 1, '45+': 2}
        flow_intensity_mapping = {"None": 0, "light": 1, "moderate": 2, "heavy": 3, "very_heavy": 4}
        for k in request.keys():
            if k == "flow_intensity":
                if request[k] is None:
                    d["flow_intensity_missing"] = 1
                    d["flow_intensity"] = 0
                else:
                    d["flow_intensity_missing"] = 0
                    d["flow_intensity"] = flow_intensity_mapping[request[k]]
                continue
            elif k == "age_group":
                d["age_group_encoded"] = age_group_mapping[request[k]]
                continue
            elif (k == "num_fibroids" or k == "fibroid_volume_ratio" or k == "ferritin_proxy") and request[k] is None:
                d[k] = DATA["medians"][k]
                continue
            elif type(request[k]) == float or type(request[k]) == int:
                if np.isnan(request[k]) or request[k] is None:
                    if k not in optional_cols:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"%s is required and cannot be None or NaN - from preprocessing step" % k
                        )
                if k in normalize_cols:
                    mean = DATA["means"][k]
                    std = DATA["stds"][k]
                    d[k] = (request[k] - mean) / std
                    continue
            elif request[k] is None:
                if k not in optional_cols:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"%s is required and cannot be None or NaN - from preprocessing step" % k
                    )
                else:
                    raise Exception(f"unhandled case: %s is required and cannot be None or NaN" % k)

            if k in d.keys():
                d[k] = request[k]

        values = [d[k] for k in cols]

        true_missing_rate = sum(1 for k in request.keys() if request[k] is None) / len(request.keys())
        # bernoulli masking for feature dropout - prevents overfitting
            # seed for same input + seed
        if self.run_config and self.run_config["missing_rate"] > 0:
            rng = np.random.default_rng(self.run_config["seed"])
            mask = rng.random(len(values)) < self.run_config["missing_rate"]
            for i, drop in enumerate(mask):
                if drop:
                    values[i] = 0.0  # or median — same fill value as your missing indicator logic
            true_missing_rate = self.run_config["missing_rate"]

        # return 1D numpy array of floats, in a fixed column order that matches what the model was trained on
        x = torch.tensor(values, dtype=torch.float32)
        return d, true_missing_rate, x
