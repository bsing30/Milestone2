"""Unit tests for ML inference service."""
import pytest
from app.app import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health endpoint returns valid JSON."""
        response = client.get("/health")
        data = response.get_json()
        assert data is not None
        assert data.get("status") == "healthy"


class TestPredictEndpoint:
    """Test prediction endpoint functionality."""

    def test_predict_valid_input_single(self, client):
        """Predict endpoint accepts valid single prediction."""
        response = client.post(
            "/predict",
            json={"features": [5.1, 3.5, 1.4, 0.2]},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "predictions" in data
        assert "labels" in data
        assert isinstance(data["predictions"], list)
        assert len(data["predictions"]) == 1
        assert data["predictions"][0] in [0, 1, 2]

    def test_predict_valid_input_batch(self, client):
        """Predict endpoint accepts valid batch prediction."""
        response = client.post(
            "/predict",
            json={
                "features": [
                    [5.1, 3.5, 1.4, 0.2],
                    [6.2, 2.9, 4.3, 1.3],
                ]
            },
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["predictions"]) == 2
        assert len(data["labels"]) == 2

    def test_predict_missing_features_returns_400(self, client):
        """Predict endpoint returns 400 when features key is missing."""
        response = client.post(
            "/predict",
            json={},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_predict_invalid_format_returns_400(self, client):
        """Predict endpoint returns 400 for invalid format."""
        response = client.post(
            "/predict",
            json={"features": "not-a-list"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_predict_content_type_json_required(self, client):
        """Predict endpoint expects JSON content."""
        response = client.post("/predict", data="invalid")
        # Flask may return 400 or 415 for wrong content type
        assert response.status_code in [400, 415, 500]


class TestInputOutputFormats:
    """Validate input/output format consistency."""

    def test_output_labels_match_class_names(self, client):
        """Output labels are valid Iris class names."""
        response = client.post(
            "/predict",
            json={"features": [5.1, 3.5, 1.4, 0.2]},
            content_type="application/json",
        )
        data = response.get_json()
        valid_labels = {"setosa", "versicolor", "virginica"}
        assert data["labels"][0] in valid_labels

    def test_predictions_and_labels_same_length(self, client):
        """Predictions and labels arrays have same length."""
        response = client.post(
            "/predict",
            json={
                "features": [
                    [5.1, 3.5, 1.4, 0.2],
                    [6.2, 2.9, 4.3, 1.3],
                ]
            },
            content_type="application/json",
        )
        data = response.get_json()
        assert len(data["predictions"]) == len(data["labels"])
