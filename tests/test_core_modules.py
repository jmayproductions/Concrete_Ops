from modules.pour_manager.pour_status import PourStatusManager

def test_pour_status_mock():
    mgr = PourStatusManager(project_id="TEST-123")
    status = mgr.get_status()
    assert status in ["pending", "active", "paused", "complete"]
