# ML Inference Service - Milestone 2

[![Build, Test, and Publish](https://github.com/bsing30/Milestone2/actions/workflows/build.yml/badge.svg)](https://github.com/bsing30/Milestone2/actions/workflows/build.yml)

Containerized ML inference service (Iris classifier) with CI/CD pipeline.

## Quick Start

### Pull and Run the Image

```bash
# Pull from GitHub Container Registry (replace with your registry if using course registry)
docker pull ghcr.io/bsing30/milestone2:v1.0.0

# Run the container
docker run -p 8080:8080 ghcr.io/bsing30/milestone2:v1.0.0
```

### Test the API

```bash
# Health check
curl http://localhost:8080/health

# Prediction
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Local Development

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized runs)

### Setup

```bash
# Clone the repository
git clone https://github.com/bsing30/Milestone2.git
cd Milestone2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt
pip install -r requirements.txt

# Train the model (generates app/model.pkl)
python train_model.py

# Run tests
pytest tests/ -v

# Run the app locally
cd app && python app.py
```

### Docker (Local Build)

```bash
# Build the image
docker build -t ml-service:local .

# Run
docker run -p 8080:8080 ml-service:local
```

### Docker Compose

```bash
docker-compose up --build
```

## API Endpoints

| Endpoint   | Method | Description                          |
|------------|--------|--------------------------------------|
| `/health`  | GET    | Health check                         |
| `/predict` | POST   | Prediction (JSON: `{"features": [[...]]}`) |

## Project Structure

```
├── .github/workflows/build.yml   # CI/CD pipeline
├── app/
│   ├── app.py                    # Inference service
│   ├── model.pkl                 # Trained model
│   └── requirements.txt          # Pinned dependencies
├── tests/
│   └── test_app.py               # Unit tests
├── Dockerfile                    # Multi-stage build
├── docker-compose.yaml           # Local development
├── README.md                     # Project docs
└── RUNBOOK.md                    # Operations guide
```

## License

MIT
