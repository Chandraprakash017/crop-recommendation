
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from pymongo import MongoClient, DESCENDING

# -------------------- Configuration --------------------

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "crop_model.joblib"
MONGO_URI = "mongodb://localhost:27017/"

DB_NAME = "crop_recommendation"

FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
]

st.set_page_config(
    page_title="Crop Recommendation System",
    page_icon="🌱",
    layout="wide",
)

# -------------------- Dashboard Header --------------------

st.title("🌱 Crop Recommendation System")

st.markdown("""
Welcome to the **Crop Recommendation Dashboard**.

Enter soil nutrient values and weather conditions to get
a crop recommendation from our trained Decision Tree model.
""")

st.caption("Machine Learning • Python • MongoDB • Streamlit")
st.divider()

# -------------------- Load Model --------------------

if not MODEL_PATH.exists():
    st.error("Model file not found. Please train the model first.")
    st.stop()


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


model = load_model()

# -------------------- Model Overview --------------------

st.subheader("📊 Model Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Algorithm", "Decision Tree")
col2.metric("Input Features", len(FEATURES))
col3.metric("Dataset Size", "2,200 rows")

st.caption(
    "The original dataset contains 2,200 records. "
    "The model uses a 70/30 train-test split."
)

# -------------------- Model Evaluation --------------------

st.divider()
st.subheader("🎯 Model Evaluation")

accuracy_client = None

try:
    accuracy_client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
    )

    accuracy_client.admin.command("ping")

    db = accuracy_client[DB_NAME]

    latest_run = db["model_runs"].find_one(
        {},
        sort=[("_id", DESCENDING)],
    )

    if latest_run:
        # Support common accuracy field names.
        accuracy = None

        for field in (
            "test_accuracy",
            "accuracy",
            "testAccuracy",
        ):
            if latest_run.get(field) is not None:
                accuracy = float(latest_run[field])
                break

        if accuracy is not None:
            # Convert decimal accuracy to percentage if needed.
            if 0 <= accuracy <= 1:
                accuracy *= 100

            st.metric("Test Accuracy", f"{accuracy:.2f}%")
        else:
            st.info(
                "Accuracy was not found in the latest model run. "
                "Check the fields stored in model_runs."
            )
    else:
        st.info("No model evaluation record found in MongoDB.")

except Exception as error:
    st.warning(f"Could not load model evaluation: {error}")

finally:
    if accuracy_client is not None:
        accuracy_client.close()

# -------------------- Crop Prediction Form --------------------

st.divider()
st.subheader("🌾 Soil and Weather Details")

with st.form("crop_form"):
    col1, col2 = st.columns(2)

    with col1:
        n = st.number_input(
            "Nitrogen (N)",
            min_value=0.0,
            value=90.0,
        )

        p = st.number_input(
            "Phosphorus (P)",
            min_value=0.0,
            value=42.0,
        )

        k = st.number_input(
            "Potassium (K)",
            min_value=0.0,
            value=43.0,
        )

        temperature = st.number_input(
            "Temperature (°C)",
            value=25.5,
        )

    with col2:
        humidity = st.number_input(
            "Humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=80.0,
        )

        ph = st.number_input(
            "Soil pH",
            min_value=0.0,
            max_value=14.0,
            value=6.5,
        )

        rainfall = st.number_input(
            "Rainfall (mm)",
            min_value=0.0,
            value=200.0,
        )

    submitted = st.form_submit_button(
        "🌱 Recommend Crop",
        use_container_width=True,
    )

# -------------------- Prediction and MongoDB Save --------------------

if submitted:
    values = {
        "N": n,
        "P": p,
        "K": k,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall,
    }

    input_data = pd.DataFrame(
        [values],
        columns=FEATURES,
    )

    prediction = str(model.predict(input_data)[0])

    st.success(f"Predicted crop: {prediction.title()}")

    st.caption(
        "This prediction is based on the training dataset "
        "and is not a guarantee of real-world crop suitability."
    )

    prediction_client = None

    try:
        prediction_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
        )

        prediction_client.admin.command("ping")

        db = prediction_client[DB_NAME]

        db["predictions"].insert_one({
            "input": values,
            "predicted_crop": prediction,
            "model": "DecisionTreeClassifier",
            "source": "Streamlit",
        })

        st.info("Prediction history saved to MongoDB.")

    except Exception as error:
        st.warning(
            f"Prediction worked, but saving failed: {error}"
        )

    finally:
        if prediction_client is not None:
            prediction_client.close()

# -------------------- Recent Prediction History --------------------

st.divider()
st.subheader("📋 Recent Prediction History")

history_client = None

try:
    history_client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
    )

    history_client.admin.command("ping")

    history_db = history_client[DB_NAME]

    records = list(
        history_db["predictions"]
        .find(
            {"source": "Streamlit"},
            {"_id": 0},
        )
        .sort("_id", DESCENDING)
        .limit(10)
    )

    if records:
        history_data = []

        for record in records:
            row = record.get("input", {}).copy()
            row["Predicted Crop"] = record.get(
                "predicted_crop",
                "Unknown",
            ).title()

            history_data.append(row)

        history_df = pd.DataFrame(history_data)

        st.dataframe(
            history_df,
            width="stretch",
            hide_index=True,
        )

        st.caption(
            "Showing the 10 most recent predictions saved by this app."
        )
    else:
        st.write("No prediction history yet.")

except Exception as error:
    st.warning(
        f"Could not load prediction history: {error}"
    )

finally:
    if history_client is not None:
        history_client.close()

# -------------------- Footer --------------------

st.divider()

st.caption(
    "Academic project • Decision Tree Classifier • "
    "Python, Scikit-learn, MongoDB and Streamlit"
)
# -------------------- Footer --------------------

st.divider()

st.markdown(
    """
    <div style="text-align: right; color: #808080; font-size: 14px;">
        Made by <strong>Chandra Prakash</strong> 🌱
    </div>
    """,
    unsafe_allow_html=True,
)