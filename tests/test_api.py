from fastapi.testclient import TestClient

from autotrain_data_forge.api.main import app


def test_parse_request_endpoint() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/parse-request",
        json={"prompt": 'Collect text from https://example.com/ about "docs"'},
    )

    assert response.status_code == 200
    assert response.json()["job"]["allowed_domains"] == ["example.com"]


def test_ui_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "AutoTrain Data Forge" in response.text
