import pytest
from core.docker_guard import _docker_guard

def test_docker_guard_exits_outside(monkeypatch):
    monkeypatch.delenv("RUNNING_IN_DOCKER", raising=False)
    
    with pytest.raises(SystemExit) as exc:
        _docker_guard("app", "cmd")
    
    assert exc.value.code == 1

def test_docker_guard_passes_inside(monkeypatch):
    monkeypatch.setenv("RUNNING_IN_DOCKER", "true")
    
    # Passes automatically if no exception is raised
    _docker_guard("app", "cmd")