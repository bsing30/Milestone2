# Milestone 1: Web & Serverless Model Serving

This project serves a scikit-learn model via a FastAPI web service and a Google
Cloud Function, then compares the two deployment patterns.

## Lifecycle Position
Data -> Training -> Model Artifact -> API Service -> Consumer

The `model.pkl` file is the trained artifact. The FastAPI and Cloud Function
load the artifact once at startup and expose a prediction API to downstream
consumers.

## Project Structure
```
.
├── main.py
├── model.pkl
├── train_model.py
├── requirements.txt
├── Dockerfile
├── cloud_function/
│   ├── main.py
│   └── requirements.txt
```

## Model Details
The model is a logistic regression classifier trained on the Iris dataset.
Features are:
1. sepal length (cm)
2. sepal width (cm)
3. petal length (cm)
4. petal width (cm)

## Local Setup
```bash
python -m venv .venv
```

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (cmd):
```cmd
.\.venv\Scripts\activate.bat
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Then:
```bash
python -m pip install -r requirements.txt
python train_model.py
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Usage
Health check:
```bash
curl http://localhost:8000/health
```

Prediction:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"features\": [5.1, 3.5, 1.4, 0.2]}"
```

Response:
```json
{"prediction": 0.0, "model_version": "v1"}
```

## Cloud Run Deployment (Container)
1. Build container:
   ```bash
   gcloud auth configure-docker REGION-docker.pkg.dev
   gcloud artifacts repositories create mlops-milestone1 \
     --repository-format=docker --location=REGION
   docker build -t REGION-docker.pkg.dev/PROJECT_ID/mlops-milestone1/m1-api:1.0 .
   docker push REGION-docker.pkg.dev/PROJECT_ID/mlops-milestone1/m1-api:1.0
   ```
2. Deploy:
   ```bash
   gcloud run deploy m1-api \
     --image REGION-docker.pkg.dev/PROJECT_ID/mlops-milestone1/m1-api:1.0 \
     --platform managed --region REGION --allow-unauthenticated
   ```

Cloud Run URL: `https://m1-api-645791648747.us-central1.run.app`
Artifact Registry image: `us-central1-docker.pkg.dev/milestone1-486213/mlops-milestone1/m1-api:1.0`

Evidence of HTTPS inference (curl or screenshot): `{"prediction":0.0,"model_version":"v1"}` (see `Screenshots/cloud_run_inference.png`)

Cold start notes: `Cold start ~9.79s; warm ~0.16s`

## Cloud Function Deployment
`cloud_function/model.pkl` is included in the repo, so no extra copy step is required.

Deploy:
```bash
gcloud functions deploy m1-predict \
  --runtime python311 --trigger-http --allow-unauthenticated \
  --entry-point predict --source cloud_function
```

Cloud Function URL: `https://us-central1-milestone1-486213.cloudfunctions.net/m1-predict`
Deployment logs evidence: `gcloud deploy output shows ACTIVE state`
Evidence of HTTPS inference (curl or screenshot): `{"model_version":"v1","prediction":0.0}` (see `Screenshots/cloud_function_inference.png`)
Cold start notes: `Cold start ~4.03s; warm ~0.26s`

## Comparative Analysis (FastAPI vs Cloud Function)
- Lifecycle differences (stateful vs stateless): `Cloud Run keeps a container instance warm and can reuse in-memory state; Cloud Function instances are more ephemeral and scale to zero quickly. Both are stateless from a request perspective, but Cloud Run behaves more like a long-lived web service.`
- Artifact loading strategies: `Both load model.pkl at startup; Cloud Run loads once per container, Cloud Function loads once per instance. Cold start penalty is tied to this load.`
- Latency characteristics (cold starts vs warm): `Cloud Run cold ~9.79s, warm ~0.16s; Cloud Function cold ~4.03s, warm ~0.26s. Cloud Run had slower cold start but faster warm response in this run.`
- Reproducibility considerations: `Cloud Run uses a pinned container image from Artifact Registry, which is highly reproducible. Cloud Functions rely on requirements.txt and buildpack, still reproducible but slightly less controlled than a fixed container image.`

## Monitoring Touchpoints
Potential monitoring hooks include request logging, latency metrics, error rates,
and model version tracking at the API layer and in the function handler.
