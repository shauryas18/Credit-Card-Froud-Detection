import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# Paths
# -----------------------------

DATASET_PATH = "dataset/creditcard.csv"
MODEL_DIR = "model"

os.makedirs(MODEL_DIR, exist_ok=True)


# -----------------------------
# Load dataset
# -----------------------------

print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())


# -----------------------------
# Check Class column
# -----------------------------

if "Class" not in df.columns:
    raise ValueError(
        "Class column not found in dataset. "
        "Make sure your CSV is the standard creditcard.csv dataset."
    )


# -----------------------------
# Features and target
# -----------------------------

X = df.drop("Class", axis=1)
y = df["Class"]


# -----------------------------
# Handle missing values
# -----------------------------

X = X.fillna(X.median())


# -----------------------------
# Train-test split
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# -----------------------------
# Scaling
# -----------------------------

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# -----------------------------
# Model
# -----------------------------

print("\nTraining model...")

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(X_train_scaled, y_train)


# -----------------------------
# Evaluation
# -----------------------------

y_pred = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# -----------------------------
# Save model
# -----------------------------

joblib.dump(
    model,
    os.path.join(MODEL_DIR, "fraud_model.pkl")
)

joblib.dump(
    scaler,
    os.path.join(MODEL_DIR, "scaler.pkl")
)

joblib.dump(
    list(X.columns),
    os.path.join(MODEL_DIR, "features.pkl")
)


print("\n================================")
print("Model saved successfully!")
print("================================")

print("model/fraud_model.pkl")
print("model/scaler.pkl")
print("model/features.pkl")