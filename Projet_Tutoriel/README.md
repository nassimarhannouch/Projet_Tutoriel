# 🎓 Système interactif d’analyse des feedbacks étudiants

Ce projet a pour objectif de faciliter la collecte, l’analyse et l’exploitation pédagogique des retours étudiants via une plateforme intelligente et interactive.

---

## 🔧 Technologies utilisées

- **Frontend** : HTML, CSS, JavaScript
- **Backend** : Django (Python)
- **API** : Django REST Framework
- **NLP / ML** :
  - TF-IDF Vectorizer
  - Naive Bayes (Français)
  - Régression Logistique (Anglais)
  - Langdetect (détection automatique de langue)
- **Dashboards** : Dash (Plotly)
- **Base de données** : MySQL
- **Chatbot intelligent** : intégré dans l’interface étudiant
- **Outils** : Git, GitHub, VS Code

---

## 🧠 Fonctionnalités principales

- 🔹 Interface étudiante avec chatbot conversationnel
- 🔹 Détection automatique de la langue (FR / EN)
- 🔹 Classification de sentiment (positif, neutre, négatif)
- 🔹 Filtrage intelligent des feedbacks non sérieux
- 🔹 Génération automatique de recommandations
- 🔹 Tableaux de bord dynamiques pour les enseignants et administrateurs
- 🔹 Gestion des utilisateurs, rôles et feedbacks

---

## ⚙️ Installation

```bash
# 1. Cloner le projet
git clone https://github.com/votre-utilisateur/feedback-analyzer.git

# 2. Accéder au dossier
cd feedback-analyzer

# 3. Créer un environnement virtuel
python -m venv env
source env/bin/activate   # ou env\Scripts\activate sous Windows

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer le serveur Django
python manage.py runserver

