# training.py – Federated Learning: train_local_model, aggregate_models


def train_local_model(data):
    # Example: train a simple model (mean of data)
    if not data:
        return {"model": None}
    mean = sum(data) / len(data)
    return {"model": mean}


def aggregate_models(models):
    # Aggregate by averaging model values
    if not models:
        return None
    values = [m["model"] for m in models if m["model"] is not None]
    if not values:
        return None
    avg = sum(values) / len(values)
    return {"model": avg}
