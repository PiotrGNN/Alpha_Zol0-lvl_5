from core.InfinityLayerLogger import InfinityLayerLogger


def test_infinity_layer_logger():
    logger = InfinityLayerLogger()
    logger.log("start", {"info": "init"})
    logger.log("decision", {"action": "buy"})
    logs = logger.get_logs()
    assert len(logs) == 2
    assert logs[0]["event"] == "start"
    assert logs[1]["details"]["action"] == "buy"
    decision_logs = logger.get_logs("decision")
    assert len(decision_logs) == 1
    assert decision_logs[0]["event"] == "decision"
    summary = logger.summary()
    assert summary["total"] == 2
    assert "start" in summary["events"]
    assert "decision" in summary["events"]
