import torch
from ..model.loader import ModelHandle
from ..pipeline.preprocess import Features

def inference(f: Features, model: ModelHandle):
    with torch.no_grad():
        logit = model(f.x)
        score = torch.sigmoid(logit).item()
    return score