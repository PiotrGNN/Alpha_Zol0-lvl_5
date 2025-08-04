from core.OmegaAudit import OmegaAudit


def test_omega_audit():
    audit = OmegaAudit()
    audit.log_decision("agent1", "buy", "success", {"price": 100})
    audit.log_decision("agent2", "sell", "fail", {"price": 90})
    entries = audit.get_entries()
    assert len(entries) == 2
    assert entries[0]["agent"] == "agent1"
    assert entries[1]["result"] == "fail"
    agent1_entries = audit.get_entries("agent1")
    assert len(agent1_entries) == 1
    assert agent1_entries[0]["decision"] == "buy"
    summary = audit.summary()
    assert summary["total"] == 2
    assert "agent1" in summary["agents"]
    assert "agent2" in summary["agents"]
