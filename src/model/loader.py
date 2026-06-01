import numpy as np
import torch
import torch.nn as nn

def load_model():
    handler = ModelHandle()
    handler.load()
    return handler.model

class ModelHandle:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.build_model().to(self.device)
    
    def build_model(self) -> nn.Module:
        return nn.Sequential(
            nn.Linear(20, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def load(self):
        state_dict = torch.load("src/model/artifacts/model.pth", map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        return self.model

