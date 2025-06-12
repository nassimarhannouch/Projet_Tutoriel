# sentiment_model.py

import joblib
import re
import os

# Déterminer le répertoire du fichier actuel
BASE_DIR = os.path.dirname(__file__)

# Charger le modèle et le vectorizer une seule fois
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'sentiment_model_fr_nb.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'model', 'vectorizer.pkl')

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

def preprocess(text):
    """Nettoyage de texte : suppression des caractères spéciaux, mise en minuscules."""
    return re.sub(r'[^\w\s]', '', text.lower())

def predict_sentiment(commentaire):
    """Prédit le sentiment d’un commentaire (ex: positif, négatif)."""
    commentaire = preprocess(commentaire)
    vect = vectorizer.transform([commentaire])
    prediction = model.predict(vect)[0]
    return prediction
