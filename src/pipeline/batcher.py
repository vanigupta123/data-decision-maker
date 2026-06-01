class Batcher:
    def __init__(self, model, batch_size: int, max_wait_ms: int):
        self.model = model
        self.batch_size = batch_size