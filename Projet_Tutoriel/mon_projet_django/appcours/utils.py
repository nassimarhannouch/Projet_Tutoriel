import re
import joblib
import os
from django.core.mail import send_mail
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer

# ----------------------------
# Prétraitement texte
# ----------------------------

def clean_text(text):
    """Nettoie le texte avant de le passer au modèle."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)  # Remplacer les espaces multiples
    text = text.lower()               # Minuscules
    text = re.sub(r'[^\w\s]', '', text)  # Supprimer la ponctuation
    return text.strip()

# ----------------------------
# Envoi d'emails
# ----------------------------

def send_email_smtp(to_email, subject, message):
    """Envoie un email via SMTP."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur d'envoi de l'email: {e}")
        return False

# ----------------------------
# Classification des thèmes par mots-clés
# ----------------------------

def classify_theme_by_keywords(text):
    """Classifie le thème basé sur des mots-clés si le modèle n'est pas disponible."""
    text = text.lower()
    
    # Dictionnaire de mots-clés pour chaque thème
    theme_keywords = {
        'workload': ['travail', 'charge', 'lourd', 'difficile', 'stress', 'pression', 'deadline', 'temps', 'surcharge'],
        'course content': ['cours', 'contenu', 'matière', 'leçon', 'programme', 'syllabus', 'curriculum', 'sujet'],
        'teacher': ['professeur', 'enseignant', 'prof', 'instructeur', 'formateur', 'pédagogie', 'explication'],
        'organization': ['organisation', 'planning', 'horaire', 'emploi du temps', 'structure', 'gestion', 'administration']
    }
    
    # Compter les correspondances pour chaque thème
    theme_scores = {}
    for theme, keywords in theme_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        theme_scores[theme] = score
    
    # Retourner le thème avec le score le plus élevé
    if max(theme_scores.values()) > 0:
        return max(theme_scores, key=theme_scores.get)
    
    return "general"

# ----------------------------
# Prédiction du thème
# ----------------------------

def predict_theme(text):
    """Prédit le thème à partir du texte à l'aide du modèle ou des mots-clés."""
    try:
        model_path = 'theme_classifiere.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            cleaned = clean_text(text)
            return model.predict([cleaned])[0]
        else:
            print("Fichier de modèle introuvable. Utilisation de la classification par mots-clés.")
            return classify_theme_by_keywords(text)
    except Exception as e:
        print(f"Erreur lors de la prédiction du thème : {e}")
        print("Basculement vers la classification par mots-clés.")
        return classify_theme_by_keywords(text)

# ----------------------------
# Génération des recommandations améliorée
# ----------------------------

def generate_recommendations_from_theme(theme, sentiment):
    """Generates recommendations based on theme and sentiment."""
    recs = []
    
    # Debug pour vérifier le sentiment reçu
    print(f"[DEBUG] Génération recommandations - Thème: {theme}, Sentiment: {sentiment}")

    if sentiment == "negative" or sentiment == "négatif":
        if theme == "workload":
            recs.append("Réduire la charge de travail excessive.")
            recs.append("Assouplir les délais de projets serrés.")
            recs.append("Proposer un meilleur équilibre travail-vie étudiante.")
        elif theme == "course content":
            recs.append("Mettre à jour le contenu du cours.")
            recs.append("Fournir plus de matériel d'apprentissage.")
            recs.append("Adapter le contenu au niveau des étudiants.")
        elif theme == "teacher":
            recs.append("Encourager l'enseignant à être plus accessible.")
            recs.append("Améliorer la qualité des explications.")
            recs.append("Former l'enseignant aux méthodes pédagogiques modernes.")
        elif theme == "organization":
            recs.append("Revoir l'organisation des horaires.")
            recs.append("Améliorer la gestion des cours et du temps.")
            recs.append("Optimiser la communication administrative.")
        elif theme == "general":
            recs.append("Analyser le feedback pour des améliorations générales.")
            recs.append("Organiser une réunion avec les étudiants concernés.")
        else:
            recs.append("Examiner attentivement ce feedback spécifique.")

    elif sentiment == "positive" or sentiment == "positif":
        if theme == "workload":
            recs.append("La charge de travail semble bien équilibrée, continuer ainsi.")
        elif theme == "course content":
            recs.append("Le contenu du cours est pertinent, le maintenir.")
        elif theme == "teacher":
            recs.append("La pédagogie de l'enseignant est appréciée.")
        elif theme == "organization":
            recs.append("L'organisation est bien structurée.")
        elif theme == "general":
            recs.append("Feedback positif général.")
        else:
            recs.append("Continuer les bonnes pratiques.")
    
    else:  # sentiment neutre ou non défini
        recs.append("Analyser ce feedback pour identifier les actions nécessaires.")

    return recs

# ----------------------------
# Traitement des feedbacks
# ----------------------------

def process_all_feedbacks():
    """
    Traite tous les feedbacks pour prédire les thèmes et générer des recommandations.
    """
    from appcours.models import Feedback

    try:
        feedbacks = Feedback.objects.all()
        processed_count = 0

        for fb in feedbacks:
            print(f"[DEBUG] Traitement du feedback ID: {fb.id}")
            
            # 1. Prédire le thème
            theme = predict_theme(fb.contenu)
            fb.theme_pred = theme
            print(f"[DEBUG] Thème prédit: {theme}")

            # 2. Générer les recommandations
            sentiment = getattr(fb, 'sentimentAnalyse', 'neutral')
            recs = generate_recommendations_from_theme(theme, sentiment)
            print(f"[DEBUG] Recommandations générées: {recs}")

            # 3. Convertir la liste en string
            fb.recommendations = "; ".join(recs)

            # 4. Sauvegarder
            fb.save()
            processed_count += 1
            print(f"[DEBUG] Feedback {fb.id} sauvegardé avec succès")

        print(f"Traitement terminé: {processed_count} feedbacks traités")
        return processed_count

    except Exception as e:
        print(f"Erreur lors du traitement des feedbacks: {e}")
        import traceback
        traceback.print_exc()
        return 0

# ----------------------------
# Traitement d'un feedback spécifique
# ----------------------------

def process_single_feedback(feedback_id):
    """Traite un feedback spécifique."""
    from appcours.models import Feedback
    
    try:
        fb = Feedback.objects.get(id=feedback_id)
        
        # 1. Prédire le thème
        theme = predict_theme(fb.contenu)
        fb.theme_pred = theme
        print(f"[DEBUG] Thème prédit pour feedback {feedback_id}: {theme}")

        # 2. Générer les recommandations
        sentiment = getattr(fb, 'sentimentAnalyse', 'neutral')
        recs = generate_recommendations_from_theme(theme, sentiment)
        print(f"[DEBUG] Recommandations pour feedback {feedback_id}: {recs}")

        # 3. Sauvegarder
        fb.recommendations = "; ".join(recs)
        fb.save()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors du traitement du feedback {feedback_id}: {e}")
        return False

# ----------------------------
# Accès aux ressources par cours
# ----------------------------

def get_resources_for_course(course_name):
    """Retourner des ressources de renforcement pour un cours."""
    try:
        from appcours.models import CourseResource
        resources = CourseResource.objects.filter(course_name=course_name)
        if resources.exists():
            return [resource.resource_link for resource in resources]
        return ["No resources found"]
    except Exception as e:
        print(f"Erreur lors de la récupération des ressources: {e}")
        return ["Error retrieving resources"]

# ----------------------------
# Extraction de mots-clés
# ----------------------------

def extract_keywords(text, top_n=5):
    """Extrait les mots-clés les plus importants à partir du texte."""
    if not text:
        return []

    try:
        # Nettoyage basique du texte
        cleaned_text = clean_text(text)
        
        if len(cleaned_text.split()) < 2:
            return cleaned_text.split()
            
        # Configuration du vectoriseur avec support français
        vectorizer = TfidfVectorizer(
            stop_words=None,  # Pas de stop words prédéfinis
            max_features=100,
            ngram_range=(1, 2)
        )
        
        X = vectorizer.fit_transform([cleaned_text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Obtenir les scores TF-IDF
        tfidf_scores = X.toarray()[0]
        
        # Créer des paires (mot, score) et trier
        word_scores = list(zip(feature_names, tfidf_scores))
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner les top_n mots-clés
        keywords = [word for word, score in word_scores[:top_n] if score > 0]
        return keywords
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des mots-clés: {e}")
        # En cas d'erreur, retourner les mots les plus fréquents
        words = text.lower().split()
        return list(set(words))[:top_n]

# ----------------------------
# Fonction utilitaire pour appel externe
# ----------------------------

def update_feedback_predictions():
    """Fonction utilitaire pour mettre à jour les prédictions des feedbacks."""
    return process_all_feedbacks()

# ----------------------------
# Fonction de diagnostic
# ----------------------------

def diagnose_feedback_processing():
    """Diagnostic pour identifier les problèmes."""
    print("=== DIAGNOSTIC DU SYSTÈME DE FEEDBACK ===")
    
    # Vérifier l'existence du modèle
    model_path = 'theme_classifier.pkl'
    print(f"Modèle ML disponible: {os.path.exists(model_path)}")
    
    # Tester la classification par mots-clés
    test_text = "Le cours est très difficile et la charge de travail est énorme"
    theme = classify_theme_by_keywords(test_text)
    print(f"Test classification par mots-clés: '{test_text}' -> {theme}")
    
    # Tester la génération de recommandations
    recs = generate_recommendations_from_theme(theme, "negative")
    print(f"Test recommandations: {recs}")
    
    return True