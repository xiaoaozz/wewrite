from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
H = {"X-User-Id": "u_test"}

def test_catalog_platforms():
    r = client.get("/api/catalog/platforms")
    assert r.status_code == 200
    ids = [x["id"] for x in r.json()]
    assert "xiaohongshu" in ids and "douyin" in ids

def test_distribute_requires_source():
    r = client.post("/api/distribute", json={"platforms": ["xiaohongshu"]}, headers=H)
    assert r.status_code == 400

def test_distribute_with_text_creates_job():
    r = client.post("/api/distribute",
                    json={"source_text": "# 源\n\n一段足够长的源内容。", "platforms": ["xiaohongshu"]},
                    headers=H)
    assert r.status_code == 200
    body = r.json()
    assert body["kind"] == "distribute"
    assert body["status"] in ("queued", "running")

def test_distribute_unknown_source_job():
    r = client.post("/api/distribute",
                    json={"source_job_id": "nope", "platforms": ["xiaohongshu"]}, headers=H)
    assert r.status_code == 404
