from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

MODEL_PATH = Path(__file__).parent / "model.pkl"


def main() -> None:
    data = load_iris()
    X, y = data.data, data.target
    model = LogisticRegression(max_iter=200, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
