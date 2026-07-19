import os
import json
import pytest
from backend.training import store

@pytest.fixture(autouse=True)
def mock_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    training_dir = data_dir / "training"
    monkeypatch.setattr(store, "DATA_DIR", str(data_dir))
    monkeypatch.setattr(store, "TRAINING_DIR", str(training_dir))
    return data_dir

def test_epd_cache():
    cache = store.EpdCache("test_policy")
    cache.put("epd1", {"p": 0.5})
    assert cache.get("epd1")["p"] == 0.5
    
    # test reload
    cache2 = store.EpdCache("test_policy")
    assert cache2.get("epd1")["p"] == 0.5

def test_jobs():
    job_id = store.create_job()
    job = store.read_job(job_id)
    assert job["id"] == job_id
    assert job["status"] == "queued"
    
    store.update_job(job_id, status="done", progress={"stage_a_done": 5})
    job2 = store.read_job(job_id)
    assert job2["status"] == "done"
    assert job2["progress"]["stage_a_done"] == 5

def test_profile():
    store.save_profile({"version": 1})
    p = store.load_profile()
    assert p["version"] == 1

def test_repertoire():
    store.save_repertoire({"targets": ["fork"]})
    assert os.path.exists(os.path.join(store.TRAINING_DIR, "repertoire.json"))

def test_drills():
    ds = {"id": "set1", "drills": [{"source": "corpus"}, {"source": "own_game"}]}
    store.save_drill_set(ds)
    loaded = store.load_drill_set("set1")
    assert loaded["id"] == "set1"
    
    sets = store.list_drill_sets()
    assert len(sets) == 1
    assert sets[0]["id"] == "set1"
    assert sets[0]["size"] == 2
    assert "corpus" in sets[0]["sources"]
