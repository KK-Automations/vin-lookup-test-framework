class TestVinApi:
    def test_decode_returns_consensus_payload(self, client):
        response = client.get("/api/v1/vin/1HGCM82633A004352")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["vin"] == "1HGCM82633A004352"
        assert payload["valid"] is True
        assert payload["fields"]["make"]["value"] == "Honda"
        assert payload["fields"]["make"]["votes"][0]["provider"] == "fake"
        assert payload["confidence"]["bucket"] in {"High", "Medium", "Low"}

    def test_invalid_vin_is_422_with_issues(self, client):
        response = client.get("/api/v1/vin/TOOSHORT")
        assert response.status_code == 422
        payload = response.get_json()
        assert payload["valid"] is False
        assert payload["issues"][0]["code"] == "length"

    def test_makes_endpoint(self, client):
        response = client.get("/api/v1/makes")
        assert response.status_code == 200
        assert "Honda" in response.get_json()["makes"]

    def test_models_requires_valid_year(self, client):
        response = client.get("/api/v1/models?make=Honda&year=abc")
        assert response.status_code == 400
