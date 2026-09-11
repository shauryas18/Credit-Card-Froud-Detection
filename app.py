import os
import sqlite3
import joblib
import numpy as np

from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# Flask Application
# =========================================================

app = Flask(__name__)

app.secret_key = "credit-card-fraud-detection-secret-key"


# =========================================================
# Paths
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "fraud.db")

MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "fraud_model.pkl"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "scaler.pkl"
)

FEATURES_PATH = os.path.join(
    MODEL_DIR,
    "features.pkl"
)


# =========================================================
# Create folders
# =========================================================

os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


# =========================================================
# Load Machine Learning Model
# =========================================================

model = None
scaler = None
features = None


def load_model():

    global model
    global scaler
    global features

    if not os.path.exists(MODEL_PATH):
        print("ERROR: fraud_model.pkl not found.")
        return False

    if not os.path.exists(SCALER_PATH):
        print("ERROR: scaler.pkl not found.")
        return False

    if not os.path.exists(FEATURES_PATH):
        print("ERROR: features.pkl not found.")
        return False

    model = joblib.load(MODEL_PATH)

    scaler = joblib.load(SCALER_PATH)

    features = joblib.load(FEATURES_PATH)

    print("Machine learning model loaded successfully.")

    print("Features:")
    print(features)

    return True


load_model()


# =========================================================
# Database Connection
# =========================================================

def get_db():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# Initialize Database
# =========================================================

def init_database():

    connection = get_db()

    cursor = connection.cursor()


    # Users table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            created_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # Transactions table

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            amount REAL NOT NULL,

            prediction TEXT NOT NULL,

            probability REAL,

            transaction_data TEXT,

            created_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
            REFERENCES users(id)

        )
    """)


    connection.commit()

    connection.close()


init_database()


# =========================================================
# FRONTEND
# =========================================================

@app.route("/")
def index():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


@app.route("/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message":
            "Invalid request."

        }), 400


    name = data.get(
        "name",
        ""
    ).strip()


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    if not name or not email or not password:

        return jsonify({

            "success": False,

            "message":
            "All fields are required."

        }), 400


    if len(password) < 6:

        return jsonify({

            "success": False,

            "message":
            "Password must contain at least 6 characters."

        }), 400


    connection = get_db()

    cursor = connection.cursor()


    try:

        hashed_password = generate_password_hash(
            password
        )


        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password
            )
        )


        connection.commit()


        return jsonify({

            "success": True,

            "message":
            "Registration successful."

        })


    except sqlite3.IntegrityError:

        return jsonify({

            "success": False,

            "message":
            "Email already registered."

        }), 409


    finally:

        connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message":
            "Invalid request."

        }), 400


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    if not email or not password:

        return jsonify({

            "success": False,

            "message":
            "Email and password are required."

        }), 400


    connection = get_db()

    cursor = connection.cursor()


    user = cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()


    connection.close()


    if user is None:

        return jsonify({

            "success": False,

            "message":
            "Invalid email or password."

        }), 401


    if not check_password_hash(
        user["password"],
        password
    ):

        return jsonify({

            "success": False,

            "message":
            "Invalid email or password."

        }), 401


    session["user_id"] = user["id"]

    session["user_name"] = user["name"]

    session["user_email"] = user["email"]


    return jsonify({

        "success": True,

        "message":
        "Login successful.",

        "user": {

            "id": user["id"],

            "name": user["name"],

            "email": user["email"]

        }

    })


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/api/logout",
    methods=["POST"]
)
def logout():

    session.clear()


    return jsonify({

        "success": True,

        "message":
        "Logged out successfully."

    })


# =========================================================
# CURRENT USER
# =========================================================

@app.route(
    "/api/user",
    methods=["GET"]
)
def current_user():

    if "user_id" not in session:

        return jsonify({

            "logged_in": False

        })


    return jsonify({

        "logged_in": True,

        "user": {

            "id":
            session["user_id"],

            "name":
            session["user_name"],

            "email":
            session["user_email"]

        }

    })


# =========================================================
# FRAUD PREDICTION
# =========================================================

@app.route(
    "/api/predict",
    methods=["POST"]
)
def predict():

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "message":
            "Please login first."

        }), 401


    if model is None:

        return jsonify({

            "success": False,

            "message":
            "Model not available. Run train_model.py first."

        }), 500


    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "message":
            "No transaction data received."

        }), 400


    try:

        values = []


        # Get features in exact training order

        for feature in features:

            value = data.get(feature)


            if value is None:

                return jsonify({

                    "success": False,

                    "message":
                    f"Missing feature: {feature}"

                }), 400


            values.append(
                float(value)
            )


        # Convert to NumPy

        input_data = np.array(
            values,
            dtype=float
        ).reshape(1, -1)


        # Scale input

        input_scaled = scaler.transform(
            input_data
        )


        # Prediction

        prediction = model.predict(
            input_scaled
        )[0]


        # Probability

        probability = None


        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = model.predict_proba(
                input_scaled
            )[0]


            probability = float(
                probabilities[1]
            )


        # Convert prediction

        if int(prediction) == 1:

            result = "Fraud"

        else:

            result = "Legitimate"


        # Transaction amount

        amount = float(
            data.get(
                "Amount",
                0
            )
        )


        # Save transaction

        connection = get_db()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO transactions
            (
                user_id,
                amount,
                prediction,
                probability,
                transaction_data
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                amount,
                result,
                probability,
                str(data)
            )
        )


        connection.commit()

        connection.close()


        # Response

        if result == "Fraud":

            message = (
                "Transaction appears to be fraudulent."
            )

        else:

            message = (
                "Transaction appears to be legitimate."
            )


        return jsonify({

            "success": True,

            "prediction": result,

            "probability": probability,

            "message": message

        })


    except ValueError:

        return jsonify({

            "success": False,

            "message":
            "Please enter valid numeric values."

        }), 400


    except Exception as error:

        print(
            "Prediction Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
            "Prediction failed."

        }), 500


# =========================================================
# TRANSACTION HISTORY
# =========================================================

@app.route(
    "/api/history",
    methods=["GET"]
)
def history():

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "message":
            "Please login first."

        }), 401


    connection = get_db()

    cursor = connection.cursor()


    rows = cursor.execute(
        """
        SELECT
            id,
            amount,
            prediction,
            probability,
            created_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()


    connection.close()


    transactions = []


    for row in rows:

        transactions.append({

            "id":
            row["id"],

            "amount":
            row["amount"],

            "prediction":
            row["prediction"],

            "probability":
            row["probability"],

            "created_at":
            row["created_at"]

        })


    return jsonify({

        "success": True,

        "transactions":
        transactions

    })


# =========================================================
# DASHBOARD
# =========================================================

@app.route(
    "/api/dashboard",
    methods=["GET"]
)
def dashboard():

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "message":
            "Please login first."

        }), 401


    connection = get_db()

    cursor = connection.cursor()


    user_id = session["user_id"]


    # Total

    total = cursor.execute(
        """
        SELECT COUNT(*)
        FROM transactions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]


    # Fraud

    fraud = cursor.execute(
        """
        SELECT COUNT(*)
        FROM transactions
        WHERE user_id = ?
        AND prediction = 'Fraud'
        """,
        (user_id,)
    ).fetchone()[0]


    # Legitimate

    legitimate = cursor.execute(
        """
        SELECT COUNT(*)
        FROM transactions
        WHERE user_id = ?
        AND prediction = 'Legitimate'
        """,
        (user_id,)
    ).fetchone()[0]


    # Recent transactions

    recent = cursor.execute(
        """
        SELECT
            id,
            amount,
            prediction,
            probability,
            created_at
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()


    connection.close()


    recent_transactions = []


    for row in recent:

        recent_transactions.append({

            "id":
            row["id"],

            "amount":
            row["amount"],

            "prediction":
            row["prediction"],

            "probability":
            row["probability"],

            "created_at":
            row["created_at"]

        })


    # Fraud percentage

    if total > 0:

        fraud_percentage = (
            fraud / total
        ) * 100

    else:

        fraud_percentage = 0


    return jsonify({

        "success": True,

        "statistics": {

            "total": total,

            "fraud": fraud,

            "legitimate": legitimate,

            "fraud_percentage":
            round(
                fraud_percentage,
                2
            )

        },

        "recent":
        recent_transactions

    })


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    print("")
    print("==========================================")
    print(" CREDIT CARD FRAUD DETECTION SYSTEM")
    print("==========================================")
    print("Model loaded:", model is not None)
    print("Frontend:", FRONTEND_DIR)
    print("Database:", DATABASE_PATH)
    print("==========================================")
    print("Open this URL:")
    print("http://127.0.0.1:5000")
    print("==========================================")
    print("")
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

  
