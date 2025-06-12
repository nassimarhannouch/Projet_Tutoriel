from flask import Flask, request, jsonify
from flask_cors import CORS
from langdetect import detect, LangDetectException
import joblib

app = Flask(__name__)
CORS(app)

model_fr = joblib.load("modele_serieux_fr.joblib")
model_en = joblib.load("modele_serieux_ang.joblib")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    feedback = data.get("feedback", "")

    if not feedback.strip():
        print("Feedback vide reçu.")
        return jsonify({"serieux": 0, "langue_detectee": "undefined"})

    try:
        langue = detect(feedback)
        print(f"Langue détectée : {langue}")
    except LangDetectException:
        print("Erreur détection langue.")
        langue = "undefined"

    if langue == "fr":
        prediction = model_fr.predict([feedback])[0]
        print(f"Prédiction modèle français : {prediction}")
    elif langue == "en":
        prediction = model_en.predict([feedback])[0]
        print(f"Prédiction modèle anglais : {prediction}")
    else:
        prediction = 0
        print(f"Langue inconnue : {langue}, prédiction par défaut : {prediction}")

    return jsonify({"serieux": int(prediction), "langue_detectee": langue})

if __name__ == "__main__":
    app.run(debug=True)
