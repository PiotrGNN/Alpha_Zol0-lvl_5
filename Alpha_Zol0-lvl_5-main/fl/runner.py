# runner.py – Symulacja klientów FL, aktualizacja modelu globalnego


def run_fl_round(clients, global_model):
    # Simulate FL round: each client trains, then aggregate
    from fl.training import aggregate_models, train_local_model

    local_models = [train_local_model(client["data"]) for client in clients]
    new_global = aggregate_models(local_models)
    return new_global
