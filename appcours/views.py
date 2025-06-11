from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from .models import Filiere, Utilisateur
from django.views.decorators.http import require_http_methods
from django.db import transaction
import joblib
from langdetect import detect
from django.core.paginator import Paginator
from django_plotly_dash import DjangoDash
from appcours.dashboard import create_student_dashboard
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
import joblib
from langdetect import detect
from django.core.paginator import Paginator
from django_plotly_dash import DjangoDash
from appcours.dashboard import create_student_dashboard

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours, Professeur, Feedback
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import Feedback, Utilisateur, Role
from .forms import FeedbackForm
from .utils import  generate_recommendations_from_theme

from .models import Feedback, Utilisateur, Role
from .forms import FeedbackForm
from .utils import generate_recommendations_from_theme

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from appcours.forms import FeedbackForm
from appcours.models import Utilisateur, Role
from appcours.utils import  predict_theme, generate_recommendations_from_theme
from django.utils import timezone

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cours, Professeur, Feedback



from .models import Feedback, Cours, Professeur, Filiere, Promotion

User = get_user_model()

# Chemins des modèles NLP - assurez-vous que ces chemins sont corrects en production
model_en_path = r'C:/Users/Lenovo/Downloads/projet tutor/nlp_logistic_sentiment_model.pkl'
model_fr_path = r'C:/Users/Lenovo/Downloads/projet tutor/sentiment_model_fr_nb.pkl'

# Charger les modèles NLP
try:
    model_en = joblib.load(model_en_path)
    model_fr = joblib.load(model_fr_path)
except Exception as e:
    print(f"Erreur lors du chargement des modèles NLP: {e}")
    # Définir des modèles fictifs en cas d'erreur
    class DummyModel:
        def predict(self, _):
            return ['neutre']
    model_en = model_fr = DummyModel()

# Fonction pour détecter la langue et analyser le sentiment
def detect_sentiment(commentaire):
    if not commentaire or len(commentaire.strip()) == 0:
        return 'neutre'
    
    try:
        langue = detect(commentaire)
    except:
        langue = 'fr'  # Par défaut, on suppose français si la détection échoue
    
    try:
        if langue == 'fr':
            prediction = model_fr.predict([commentaire])[0]
        else:
            prediction = model_en.predict([commentaire])[0]
        
        # Normalisation du résultat
        if 'positif' in str(prediction).lower() or 'positive' in str(prediction).lower():
            return 'positif'
        elif 'negatif' in str(prediction).lower() or 'negative' in str(prediction).lower():
            return 'négatif'
        else:
            return 'neutre'
    except Exception as e:
        print(f"Erreur d'analyse de sentiment: {e}")
        return 'neutre'

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            # Redirection selon le rôle
            if user.role == 'etudiant':
                return redirect('dashboard')
            elif user.role == 'chef_filiere':
                return redirect('dashboard_chef')
            elif user.role == 'administrateur':
                return redirect('Dashadmin')
            else:
                messages.error(request, "Rôle inconnu.")
        else:
            messages.error(request, "Email ou mot de passe invalide.")
    
    return render(request, 'monapp/login.html')

def register_etudiant(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        telephone = request.POST.get('telephone')
        filiere_id = request.POST.get('filiere')
        promotion_id = request.POST.get('promotion')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('register_etudiant')

        # Vérifier si une filière a été sélectionnée
        filiere = None
        if filiere_id:
            try:
                filiere = Filiere.objects.get(pk=filiere_id)
            except Filiere.DoesNotExist:
                messages.error(request, "La filière sélectionnée n'existe pas.")
                return redirect('register_etudiant')
        
        # Vérifier si une promotion a été sélectionnée
        promotion = None
        if promotion_id:
            try:
                promotion = Promotion.objects.get(pk=promotion_id)
            except Promotion.DoesNotExist:
                messages.error(request, "La promotion sélectionnée n'existe pas.")
                return redirect('register_etudiant')

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            telephone=telephone,
            role='etudiant',
            filiere=filiere,
            promotion=promotion,
            is_active=False  # Compte inactif jusqu'à confirmation
        )
        
        # Créer un lien de confirmation
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_str(user.pk).encode())
        domain = get_current_site(request).domain
        link = f"http://{domain}/confirm/{uid}/{token}/"

        # Envoi de l'email
        subject = "Confirmez votre inscription"
        message = render_to_string('monapp/confirmation_email.html', {
            'user': user,
            'link': link,
        })
        try:
            send_mail(subject, message, 'no-reply@feedbackflow.com', [email])
            messages.success(request, "Compte créé avec succès. Vérifiez votre e-mail pour confirmer votre inscription.")
        except Exception as e:
            messages.warning(request, f"Compte créé, mais impossible d'envoyer l'email de confirmation: {str(e)}")
        
        return redirect('login')

    # Récupérer les filières et promotions pour le formulaire
    filieres = Filiere.objects.all()
    promotions = Promotion.objects.all()
    
    return render(request, 'monapp/register.html', {
        'filieres': filieres,
        'promotions': promotions
    })

def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a été confirmé. Vous pouvez maintenant vous connecter.")
        return redirect('login')
    else:
        messages.error(request, "Le lien de confirmation est invalide ou a expiré.")
        return redirect('home')
    
@login_required
def etudiant_dashboard(request):
    utilisateur = request.user
    
    # Vérifier que l'utilisateur a un rôle étudiant
    if utilisateur.role != 'etudiant':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('home')
    
    filiere = utilisateur.filiere
    if not filiere:
        messages.warning(request, "Vous n'êtes associé à aucune filière. Veuillez mettre à jour votre profil.")
        return redirect('profil_etudiant')
    
    cours = Cours.objects.filter(filiere=filiere)
    professeurs = Professeur.objects.filter(cours__in=cours).distinct()
    
    # Feedbacks envoyés par l'étudiant (non anonymes ou non)
    # Ajout de print pour debug
    feedbacks_perso = Feedback.objects.filter(etudiant=utilisateur)
    print(f"Nombre de feedbacks trouvés: {feedbacks_perso.count()}")
    
    # Si aucun feedback n'est trouvé, vérifier s'il y a des feedbacks sans cette condition
    if feedbacks_perso.count() == 0:
        all_feedbacks = Feedback.objects.all()
        print(f"Nombre total de feedbacks dans la base: {all_feedbacks.count()}")
        
        # Vérifier si l'utilisateur existe dans la table des feedbacks
        users_with_feedbacks = set(Feedback.objects.values_list('etudiant_id', flat=True))
        print(f"IDs des utilisateurs avec feedbacks: {users_with_feedbacks}")
        print(f"ID de l'utilisateur actuel: {utilisateur.id}")
    
    # Statistiques
    nombre_cours = cours.count()
    nombre_professeurs = professeurs.count()
    nombre_feedbacks = feedbacks_perso.count()
    sentiments = {
        'positif': feedbacks_perso.filter(sentiment='positif').count(),
        'neutre': feedbacks_perso.filter(sentiment='neutre').count(),
        'négatif': feedbacks_perso.filter(sentiment='négatif').count(),
    }
    
    # Pagination des feedbacks personnels (si nécessaire)
    paginator = Paginator(feedbacks_perso, 10)  # Augmenté à 10 par page pour voir plus de résultats
    page_number = request.GET.get('page')
    feedbacks_page = paginator.get_page(page_number)
    
    context = {
        'etudiant': utilisateur,
        'cours': cours,
        'professeurs': professeurs,
        'feedbacks': feedbacks_page,  # Feedbacks paginés pour l'affichage
        'nombre_cours': nombre_cours,
        'nombre_professeurs': nombre_professeurs,
        'nombre_feedbacks': nombre_feedbacks,
        'sentiments': sentiments,
        'cours_disponibles': cours,  # Pour le filtre dans le template
    }
    
    return render(request, 'monapp/etudiant_dashboard.html', context)


def detect_sentiment(commentaire):
    """
    Appelle l'API Flask pour détecter si le commentaire est négatif (serieux = 1)
    ou positif (serieux = 0).
    Retourne 'négatif' ou 'positif'.
    """
    api_url = "http://127.0.0.1:5000/predict"
    try:
        response = requests.post(api_url, json={"feedback": commentaire})
        data = response.json()
        if data.get("serieux", 0) == 1:
            return 'négatif'
        else:
            return 'positif'
    except Exception as e:
        # En cas d'erreur, on considère le feedback comme sérieux (négatif) pour prudence
        return 'négatif'

@login_required
def soumettre_feedback(request):
    """
    Fonction unifiée pour soumettre un feedback étudiant
    Combine la validation, la prédiction de thème, les recommandations et les notifications
    """
    utilisateur = request.user
    
    # Vérification du rôle utilisateur
    if utilisateur.role != 'etudiant':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('home')
    
    # Vérification de l'association à une filière
    if not utilisateur.filiere:
        messages.warning(request, "Vous n'êtes associé à aucune filière.")
        return redirect('profil_etudiant')
    
    cours_disponibles = Cours.objects.filter(filiere=utilisateur.filiere)
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        cours_id = request.POST.get('cours')
        professeur_id = request.POST.get('professeur')
        commentaire = request.POST.get('commentaire', '').strip()
        suggestions = request.POST.get('suggestions', '').strip()
        date_cours = request.POST.get('date_cours')
        note = request.POST.get('note')
        anonyme = request.POST.get('anonyme') == '1'
        partager = request.POST.get('partager') == '1'
        
        # Validation des champs requis
        if not cours_id or not note or not commentaire:
            messages.error(request, "Veuillez remplir tous les champs requis.")
            return render(request, 'monapp/soumettre_feedback.html', {
                'cours_disponibles': cours_disponibles,
                'utilisateur': utilisateur
            })
        
        # Validation de la note
        try:
            note = int(note)
            if note < 1 or note > 5:
                raise ValueError
        except ValueError:
            messages.error(request, "La note doit être entre 1 et 5.")
            return render(request, 'monapp/soumettre_feedback.html', {
                'cours_disponibles': cours_disponibles,
                'utilisateur': utilisateur
            })
        
        # Récupération des objets cours et professeur
        cours = get_object_or_404(Cours, pk=cours_id, filiere=utilisateur.filiere)
        professeur = get_object_or_404(Professeur, pk=professeur_id) if professeur_id else None
        
        # Vérification que le professeur enseigne ce cours
        if professeur and not professeur.cours.filter(id=cours_id).exists():
            messages.error(request, "Ce professeur n'enseigne pas ce cours.")
            return render(request, 'monapp/soumettre_feedback.html', {
                'cours_disponibles': cours_disponibles,
                'utilisateur': utilisateur
            })
        
        try:
            # Détection du sentiment
            sentiment = detect_sentiment(commentaire)
            
            # Si le feedback est négatif, redirection vers validation chatbot
            if sentiment == 'négatif':
                request.session['pending_feedback'] = {
                    'cours_id': cours_id,
                    'professeur_id': professeur_id,
                    'commentaire': commentaire,
                    'suggestions': suggestions,
                    'date_cours': date_cours,
                    'note': note,
                    'anonyme': anonyme,
                    'partager': partager,
                    'sentiment': sentiment
                }
                return redirect('chat_validation')
            
            # Prédiction du thème
            theme = predict_theme(commentaire)
            
            # Génération des recommandations
            recommendations = generate_recommendations_from_theme(theme)
            recommendations_text = "; ".join(recommendations)
            
            # Création du feedback
            feedback = Feedback.objects.create(
                cours=cours,
                professeur=professeur,
                etudiant=None if anonyme else utilisateur,
                note=note,
                commentaire=commentaire,
                suggestions=suggestions,
                date_cours=date_cours,
                sentiment=sentiment,
                anonyme=anonyme,
                partager=partager,
                theme_pred=theme,
                recommendations=recommendations_text
            )
            
            print(f"[DEBUG] Feedback sauvegardé - ID: {feedback.id}, Thème: {theme}")
            
            # Notification au chef de filière
            chef_filiere = Utilisateur.objects.filter(
                role=Role.CHEF_FILIERE,
                filiere=cours.filiere
            ).first()
            
            if chef_filiere:
                print(f"[DEBUG] Chef de filière trouvé : {chef_filiere.email}")
                
                recommandations_texte = "\n".join(f"- {rec}" for rec in recommendations)
                sujet_chef = f"Nouveau feedback pour le cours {cours.nom}"
                message_chef = f"""
Un feedback a été soumis pour le cours {cours.nom}.

Étudiant : {utilisateur.get_full_name() or utilisateur.username if not anonyme else 'Anonyme'}
Date : {feedback.date_creation.strftime('%d/%m/%Y %H:%M') if hasattr(feedback, 'date_creation') else timezone.now().strftime('%d/%m/%Y %H:%M')}
Note : {note}/5
Sentiment : {sentiment}

Contenu du feedback :
{commentaire}

Suggestions :
{suggestions or 'Aucune suggestion fournie'}

---

🎯 Thème identifié : {theme}

🎯 Recommandations proposées :
{recommandations_texte}

Merci de prendre les mesures appropriées.
                """
                
                try:
                    send_mail(
                        sujet_chef,
                        message_chef,
                        settings.DEFAULT_FROM_EMAIL,
                        [chef_filiere.email],
                        fail_silently=False
                    )
                    print("[DEBUG] Email envoyé au chef de filière")
                except Exception as e:
                    print(f"[ERROR] Email chef de filière : {e}")
                    messages.warning(request, "Feedback enregistré mais erreur lors de l'envoi de la notification au chef de filière.")
            else:
                print("[ERROR] Aucun chef de filière trouvé.")
                messages.warning(request, "Feedback enregistré mais aucun chef de filière trouvé pour cette filière.")
            
            # Email de remerciement à l'étudiant (si pas anonyme)
            if not anonyme and utilisateur.email:
                try:
                    sujet_etudiant = "Merci pour votre feedback"
                    message_etudiant = f"""
Bonjour {utilisateur.get_full_name() or utilisateur.username},

Merci pour votre retour concernant le cours {cours.nom}.

Votre feedback a été bien reçu et sera transmis aux responsables concernés.

Afin d'améliorer davantage la qualité de nos enseignements, nous vous invitons à compléter ce formulaire complémentaire :
https://docs.google.com/forms/d/e/1FAIpQLSefB-p6nEjUzE5BG37mGdSjkjaTLpVY7gqn4AG_zmWp6O1aTA/viewform?usp=sf_link

Merci beaucoup pour votre contribution !

L'équipe pédagogique
                    """
                    send_mail(
                        sujet_etudiant,
                        message_etudiant,
                        settings.DEFAULT_FROM_EMAIL,
                        [utilisateur.email],
                        fail_silently=False
                    )
                    print("[DEBUG] Email de remerciement envoyé à l'étudiant")
                except Exception as e:
                    print(f"[ERROR] Email étudiant : {e}")
                    messages.warning(request, "Feedback enregistré mais erreur lors de l'envoi du mail de remerciement.")
            
            messages.success(request, "Votre feedback a été soumis avec succès.")
            return redirect('merci_feedback')
            
        except Exception as e:
            print(f"[ERROR] Traitement du feedback : {e}")
            messages.error(request, "Une erreur est survenue lors du traitement de votre feedback.")
            return render(request, 'monapp/soumettre_feedback.html', {
                'cours_disponibles': cours_disponibles,
                'utilisateur': utilisateur
            })
    
    # GET : afficher le formulaire
    return render(request, 'monapp/soumettre_feedback.html', {
        'cours_disponibles': cours_disponibles,
        'utilisateur': utilisateur
    })


# Modifications dans views.py

@csrf_exempt
@login_required
def enregistrer_feedback_serieux(request):
    if request.method == 'POST':
        utilisateur = request.user
        data = json.loads(request.body)

        # Vérifie que le feedback est sérieux
        if data.get('serieux') != 1:
            return JsonResponse({'status': 'ignored'})

        feedback_data = request.session.pop('pending_feedback', None)
        if not feedback_data:
            return JsonResponse({'status': 'no_data'})

        cours = get_object_or_404(Cours, pk=feedback_data['cours_id'])
        professeur = get_object_or_404(Professeur, pk=feedback_data['professeur_id']) if feedback_data['professeur_id'] else None

        try:
            # Prédiction du thème pour feedback négatif sérieux
            theme = predict_theme(feedback_data['commentaire'])
            
            # Génération des recommandations basées sur le thème et sentiment
            recommendations = generate_recommendations_from_theme(theme, feedback_data['sentiment'])
            recommendations_text = "; ".join(recommendations)
            
            print(f"[DEBUG] Feedback négatif sérieux - Thème: {theme}, Recommandations: {recommendations}")

            # Création du feedback avec thème et recommandations
            feedback = Feedback.objects.create(
                cours=cours,
                professeur=professeur,
                etudiant=None if feedback_data['anonyme'] else utilisateur,
                note=feedback_data['note'],
                commentaire=feedback_data['commentaire'],
                suggestions=feedback_data['suggestions'],
                date_cours=feedback_data['date_cours'],
                sentiment=feedback_data['sentiment'],
                anonyme=feedback_data['anonyme'],
                partager=feedback_data['partager'],
                theme_pred=theme,  # Enregistrement du thème prédit
                recommendations=recommendations_text  # Enregistrement des recommandations
            )

            print(f"[DEBUG] Feedback sauvegardé avec ID: {feedback.id}")

            # Notification au professeur concerné par le cours
            if professeur and professeur.email:
                print(f"[DEBUG] Professeur trouvé : {professeur.email}")
                
                recommandations_texte = "\n".join(f"- {rec}" for rec in recommendations)
                sujet_prof = f"📋 Feedback sur votre cours - {cours.nom}"
                message_prof = f"""
Bonjour {professeur.nom} {professeur.prenom},

Vous avez reçu un nouveau feedback concernant votre cours "{cours.nom}".

Étudiant : {utilisateur.get_full_name() or utilisateur.username if not feedback_data['anonyme'] else 'Anonyme'}
Date du cours : {feedback_data['date_cours']}
Date du feedback : {timezone.now().strftime('%d/%m/%Y %H:%M')}
Note attribuée : {feedback_data['note']}/5
Sentiment : {feedback_data['sentiment']}

Commentaire de l'étudiant :
"{feedback_data['commentaire']}"

Suggestions de l'étudiant :
{feedback_data['suggestions'] or 'Aucune suggestion fournie'}

---

🎯 THÈME IDENTIFIÉ : {theme.upper()}

💡 RECOMMANDATIONS POUR AMÉLIORATION :
{recommandations_texte}

---

Ce feedback vous est transmis pour vous aider à améliorer votre enseignement.
N'hésitez pas à prendre en compte ces retours constructifs.

Cordialement,
Le système de feedback pédagogique
                """
                
                try:
                    send_mail(
                        sujet_prof,
                        message_prof,
                        settings.DEFAULT_FROM_EMAIL,
                        [professeur.email],
                        fail_silently=False
                    )
                    print("[DEBUG] Email de feedback envoyé au professeur")
                except Exception as e:
                    print(f"[ERROR] Email professeur : {e}")
            else:
                print("[ERROR] Aucun professeur trouvé ou email manquant.")

            return JsonResponse({
                'status': 'saved',
                'theme': theme,
                'recommendations': recommendations,
                'feedback_id': feedback.id
            })
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'enregistrement du feedback sérieux : {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid_method'})


@login_required
def valider_feedback_serieux(request):
    utilisateur = request.user
    data = request.session.pop('pending_feedback', None)
    if not data:
        return redirect('soumettre_feedback')

    cours = get_object_or_404(Cours, pk=data['cours_id'])
    professeur = get_object_or_404(Professeur, pk=data['professeur_id']) if data['professeur_id'] else None

    try:
        # Prédiction du thème pour feedback négatif validé
        theme = predict_theme(data['commentaire'])
        
        # Génération des recommandations
        recommendations = generate_recommendations_from_theme(theme, data['sentiment'])
        recommendations_text = "; ".join(recommendations)
        
        print(f"[DEBUG] Validation feedback sérieux - Thème: {theme}")

        # Création du feedback avec thème et recommandations
        feedback = Feedback.objects.create(
            cours=cours,
            professeur=professeur,
            etudiant=None if data['anonyme'] else utilisateur,
            note=data['note'],
            commentaire=data['commentaire'],
            suggestions=data['suggestions'],
            date_cours=data['date_cours'],
            sentiment=data['sentiment'],
            anonyme=data['anonyme'],
            partager=data['partager'],
            theme_pred=theme,  # Enregistrement du thème prédit
            recommendations=recommendations_text  # Enregistrement des recommandations
        )

        print(f"[DEBUG] Feedback validé sauvegardé avec ID: {feedback.id}")

        # Notification au professeur concerné
        if professeur and professeur.email:
            recommandations_texte = "\n".join(f"- {rec}" for rec in recommendations)
            sujet_prof = f"📋 Feedback validé sur votre cours - {cours.nom}"
            message_prof = f"""
Bonjour {professeur.nom} {professeur.prenom},

Un feedback concernant votre cours "{cours.nom}" a été validé après vérification.

Étudiant : {utilisateur.get_full_name() or utilisateur.username if not data['anonyme'] else 'Anonyme'}
Date du cours : {data['date_cours']}
Date du feedback : {timezone.now().strftime('%d/%m/%Y %H:%M')}
Note attribuée : {data['note']}/5
Sentiment : {data['sentiment']} (VALIDÉ)

Commentaire de l'étudiant :
"{data['commentaire']}"

Suggestions de l'étudiant :
{data['suggestions'] or 'Aucune suggestion fournie'}

---

🎯 THÈME IDENTIFIÉ : {theme.upper()}

💡 RECOMMANDATIONS POUR AMÉLIORATION :
{recommandations_texte}

---

Ce feedback a été validé après interaction avec notre système de vérification.
Il reflète une préoccupation légitime de l'étudiant.

Cordialement,
Le système de feedback pédagogique
            """
            
            try:
                send_mail(
                    sujet_prof,
                    message_prof,
                    settings.DEFAULT_FROM_EMAIL,
                    [professeur.email],
                    fail_silently=False
                )
                print("[DEBUG] Email de validation envoyé au professeur")
            except Exception as e:
                print(f"[ERROR] Email professeur : {e}")

        messages.success(request, f"Votre feedback a été soumis après vérification. Thème identifié: {theme}")
        return redirect('merci_feedback')
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la validation : {e}")
        messages.error(request, "Erreur lors de la validation du feedback.")
        return redirect('soumettre_feedback')


# Modification dans la fonction chat_validation pour inclure thème et recommandations
@login_required
def chat_validation(request):
    """
    Gestion de la validation par chatbot pour les feedbacks négatifs
    """
    feedback_data = request.session.get('pending_feedback')
    if not feedback_data:
        messages.warning(request, "Aucun feedback en attente de validation.")
        return redirect('soumettre_feedback')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm':
            try:
                cours = get_object_or_404(Cours, pk=feedback_data['cours_id'])
                professeur = get_object_or_404(Professeur, pk=feedback_data['professeur_id']) if feedback_data['professeur_id'] else None
                
                # Prédiction du thème et recommandations
                theme = predict_theme(feedback_data['commentaire'])
                recommendations = generate_recommendations_from_theme(theme, feedback_data['sentiment'])
                
                print(f"[DEBUG] Confirmation chat - Thème: {theme}")

                feedback = Feedback.objects.create(
                    cours=cours,
                    professeur=professeur,
                    etudiant=None if feedback_data['anonyme'] else request.user,
                    note=feedback_data['note'],
                    commentaire=feedback_data['commentaire'],
                    suggestions=feedback_data['suggestions'],
                    date_cours=feedback_data['date_cours'],
                    sentiment=feedback_data['sentiment'],
                    anonyme=feedback_data['anonyme'],
                    partager=feedback_data['partager'],
                    theme_pred=theme,  # Enregistrement du thème
                    recommendations="; ".join(recommendations)  # Enregistrement des recommandations
                )
                
                # Notification au professeur concerné
                if professeur and professeur.email:
                    recommandations_texte = "\n".join(f"- {rec}" for rec in recommendations)
                    sujet_prof = f"📋 Feedback confirmé sur votre cours - {cours.nom}"
                    message_prof = f"""
Bonjour {professeur.nom} {professeur.prenom},

Un feedback concernant votre cours "{cours.nom}" a été confirmé après validation interactive.

Étudiant : {request.user.get_full_name() or request.user.username if not feedback_data['anonyme'] else 'Anonyme'}
Date du cours : {feedback_data['date_cours']}
Date du feedback : {timezone.now().strftime('%d/%m/%Y %H:%M')}
Note attribuée : {feedback_data['note']}/5
Sentiment : {feedback_data['sentiment']} (CONFIRMÉ)

Commentaire de l'étudiant :
"{feedback_data['commentaire']}"

Suggestions de l'étudiant :
{feedback_data['suggestions'] or 'Aucune suggestion fournie'}

---

🎯 THÈME IDENTIFIÉ : {theme.upper()}

💡 RECOMMANDATIONS POUR AMÉLIORATION :
{recommandations_texte}

---

Ce feedback a été confirmé après un processus de validation interactive.

Cordialement,
Le système de feedback pédagogique
                    """
                    
                    try:
                        send_mail(
                            sujet_prof,
                            message_prof,
                            settings.DEFAULT_FROM_EMAIL,
                            [professeur.email],
                            fail_silently=False
                        )
                        print("[DEBUG] Email de confirmation envoyé au professeur")
                    except Exception as e:
                        print(f"[ERROR] Email professeur : {e}")
                
                # Nettoyage de la session
                del request.session['pending_feedback']
                
                messages.success(request, f"Votre feedback a été soumis avec succès après validation. Thème identifié: {theme}")
                return redirect('merci_feedback')
                
            except Exception as e:
                print(f"[ERROR] Validation feedback : {e}")
                messages.error(request, "Erreur lors de la validation du feedback.")
        
        elif action == 'cancel':
            del request.session['pending_feedback']
            messages.info(request, "Feedback annulé.")
            return redirect('soumettre_feedback')
    
    return render(request, 'monapp/chat.html', {
        'commentaire': feedback_data['commentaire'],
        'cours_id': feedback_data['cours_id']
    })




@login_required
def get_professeurs_by_cours(request, cours_id):
    try:
        # Récupérer le cours
        cours = get_object_or_404(Cours, pk=cours_id)
        
        # Vérifier que l'utilisateur a accès à ce cours
        if request.user.filiere != cours.filiere and request.user.role == 'etudiant':
            return JsonResponse({'error': 'Vous n\'avez pas accès à ce cours.'}, status=403)
        
        # Récupérer les professeurs qui enseignent ce cours
        professeurs = Professeur.objects.filter(cours=cours).values('id', 'nom', 'prenom')
        return JsonResponse(list(professeurs), safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@login_required
def chef_filiere_dashboard(request):
    # Vérifier que l'utilisateur a un rôle chef de filière
    if request.user.role != 'chef_filiere':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('home')
    
    chef_filiere = request.user
    filiere = chef_filiere.filiere
    
    # Si le chef de filière n'est pas associé à une filière
    if not filiere:
        messages.warning(request, "Vous n'êtes associé à aucune filière. Contactez un administrateur.")
        return redirect('home')
    
    # Récupérer les cours de la filière
    cours = Cours.objects.filter(filiere=filiere)
    
    # Récupérer les professeurs qui enseignent ces cours
    professeurs = Professeur.objects.filter(cours__in=cours).distinct()
    
    # Récupérer tous les feedbacks pour les cours de la filière
    feedbacks = Feedback.objects.filter(cours__in=cours)
    
    # Statistiques générales
    nombre_cours = cours.count()
    nombre_professeurs = professeurs.count()
    nombre_feedbacks = feedbacks.count()
    
    # Note moyenne par cours
    notes_par_cours = {}
    for c in cours:
        feedbacks_cours = feedbacks.filter(cours=c)
        if feedbacks_cours.exists():
            note_moyenne = sum(f.note for f in feedbacks_cours) / feedbacks_cours.count()
            notes_par_cours[c.nom] = round(note_moyenne, 1)
        else:
            notes_par_cours[c.nom] = "Pas de feedback"
    
    # Distribution des sentiments
    sentiments = {
        'positif': feedbacks.filter(sentiment='positif').count(),
        'neutre': feedbacks.filter(sentiment='neutre').count(),
        'négatif': feedbacks.filter(sentiment='négatif').count(),
    }
    
    context = {
        'chef_filiere': chef_filiere,
        'filiere': filiere,
        'cours': cours,
        'professeurs': professeurs,
        'feedbacks': feedbacks,
        'nombre_cours': nombre_cours,
        'nombre_professeurs': nombre_professeurs,
        'nombre_feedbacks': nombre_feedbacks,
        'notes_par_cours': notes_par_cours,
        'sentiments': sentiments
    }
    
    return render(request, 'monapp/chef_filiere_dashboard.html', context)

@login_required
def admin_dashboard(request):
    # Vérifier que l'utilisateur a un rôle administrateur
    if request.user.role != 'administrateur':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('home')
    
    # Statistiques globales
    filieres = Filiere.objects.all()
    cours = Cours.objects.all()
    professeurs = Professeur.objects.all()
    etudiants = User.objects.filter(role='etudiant')
    feedbacks = Feedback.objects.all()
    
    context = {
        'filieres': filieres,
        'cours': cours,
        'professeurs': professeurs,
        'etudiants': etudiants,
        'feedbacks': feedbacks,
        'nombre_filieres': filieres.count(),
        'nombre_cours': cours.count(),
        'nombre_professeurs': professeurs.count(),
        'nombre_etudiants': etudiants.count(),
        'nombre_feedbacks': feedbacks.count()
    }
    
    return render(request, 'monapp/admin_dashboard.html', context)

def home(request):
    return render(request, 'monapp/home.html')

def contact_view(request):
    return render(request, 'monapp/contact.html')

def about_view(request):
    return render(request, 'monapp/about.html')

@login_required
def profil_etudiant(request):
    utilisateur = request.user
    
    if request.method == 'POST':
        # Mise à jour du profil
        utilisateur.first_name = request.POST.get('first_name', utilisateur.first_name)
        utilisateur.last_name = request.POST.get('last_name', utilisateur.last_name)
        utilisateur.telephone = request.POST.get('telephone', utilisateur.telephone)
        
        # Mise à jour du mot de passe si fourni
        new_password = request.POST.get('new_password')
        if new_password:
            current_password = request.POST.get('current_password')
            if utilisateur.check_password(current_password):
                utilisateur.set_password(new_password)
                messages.success(request, "Mot de passe mis à jour avec succès.")
            else:
                messages.error(request, "Mot de passe actuel incorrect.")
                return redirect('profil_etudiant')
        
        utilisateur.save()
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('profil_etudiant')
    
    return render(request, 'monapp/profil.html', {'utilisateur': utilisateur})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def merci_feedback(request):
    return render(request, 'monapp/merci_feedback.html')

@login_required
def dashboard_view(request):
    """
    Vue pour afficher le dashboard de l'étudiant.
    Cette vue charge le dashboard django-plotly-dash avec l'ID de l'utilisateur connecté.
    """
    # Vérifier que l'utilisateur est un étudiant
    if request.user.role != 'etudiant':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('home')
    
    # Récupération de l'ID de l'utilisateur connecté
    user_id = request.user.id
    
    # Création ou récupération de l'application dashboard pour cet utilisateur
    app_name = f'StudentDashboard_{user_id}'
    
    # Vérifier si l'app existe déjà, sinon la créer
    try:
        # Essayer de récupérer l'app existante
        app = DjangoDash._by_name.get(app_name)
        if app is None:
            # Créer une nouvelle app si elle n'existe pas
            app = create_student_dashboard(user_id, app_name)
    except Exception as e:
        # Créer l'app en cas d'erreur
        try:
            app = create_student_dashboard(user_id, app_name)
        except Exception as create_error:
            messages.error(request, f"Erreur lors de la création du dashboard: {str(create_error)}")
            return redirect('etudiant_dashboard')  # Rediriger vers le dashboard principal
    
    # Contexte pour le template
    context = {
        'user_id': user_id,
        'app_name': app_name,  # Nom de l'app Dash à intégrer
        'utilisateur': request.user,
    }
    
    # IMPORTANT: Retourner une réponse HTTP
    return render(request, 'monapp/dashboard.html', context)
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django_plotly_dash import DjangoDash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# Couleurs pour les graphiques
colors_list = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']

def get_etudiant_info(user_id):
    """Récupère les informations d'un étudiant"""
    try:
        from .models import Utilisateur
        etudiant = Utilisateur.objects.get(id=user_id, role='etudiant')
        return {
            'id': etudiant.id,
            'username': etudiant.username,
            'email': etudiant.email,
            'filiere_id': etudiant.filiere.id if etudiant.filiere else None,
            'filiere_nom': etudiant.filiere.nom if etudiant.filiere else None,
            'promotion_id': etudiant.promotion.id if etudiant.promotion else None,
            'promotion_nom': etudiant.promotion.nom if etudiant.promotion else None,
        }
    except Utilisateur.DoesNotExist:
        return None

def get_cours_filiere(filiere_id):
    """Récupère les cours d'une filière avec leurs professeurs"""
    if not filiere_id:
        return []
    
    from .models import Cours
    cours_list = []
    cours_filiere = Cours.objects.filter(filiere_id=filiere_id).prefetch_related('professeurs')
    
    for cours in cours_filiere:
        professeurs_data = []
        for prof in cours.professeurs.all():
            professeurs_data.append({
                'prof_nom': prof.nom,
                'prof_prenom': prof.prenom,
                'prof_email': prof.email
            })
        
        cours_list.append({
            'cours_nom': cours.nom,
            'professeurs': professeurs_data
        })
    
    return cours_list

def get_ressources_cours(cours_nom):
    """Récupère les ressources d'un cours"""
    from .models import CourseResource
    ressources = CourseResource.objects.filter(course_name=cours_nom)
    return [{'description': r.description, 'link': r.resource_link} for r in ressources]

def get_notes_et_moyennes(user_id):
    """Récupère les notes et moyennes d'un étudiant"""
    from .models import Notes, Cours
    from django.db.models import Avg
    
    notes_etudiant = Notes.objects.filter(etudiant_id=user_id).select_related('cours')
    data = []
    
    for note in notes_etudiant:
        # Calculer la moyenne de la classe pour ce cours
        moyenne_classe = Notes.objects.filter(cours=note.cours).aggregate(
            moyenne=Avg('note')
        )['moyenne'] or 0
        
        data.append({
            'Cours': note.cours.nom,
            'Notes': float(note.note),
            'Moyenne Classe': round(float(moyenne_classe), 2)
        })
    
    return data

def get_modes_evaluation(filiere_id):
    """Récupère les modes d'évaluation pour une filière"""
    from .models import ModeEvaluation, Cours
    
    if not filiere_id:
        return {'labels': ['TP', 'Examen', 'Projet'], 'values': [10, 70, 20]}
    
    # Récupérer tous les modes d'évaluation des cours de la filière
    modes = ModeEvaluation.objects.filter(cours__filiere_id=filiere_id)
    
    if not modes.exists():
        return {'labels': ['TP', 'Examen', 'Projet'], 'values': [10, 70, 20]}
    
    # Grouper par mode et calculer la moyenne des pourcentages
    modes_dict = {}
    for mode in modes:
        if mode.mode in modes_dict:
            modes_dict[mode.mode].append(mode.pourcentage)
        else:
            modes_dict[mode.mode] = [mode.pourcentage]
    
    labels = list(modes_dict.keys())
    values = [sum(percentages) / len(percentages) for percentages in modes_dict.values()]
    
    return {'labels': labels, 'values': values}

def create_evaluation_charts(filiere_id=None):
    """Crée un graphique d'évaluation pour une filière"""
    data = get_modes_evaluation(filiere_id)
    
    fig = go.Figure(
        data=[go.Pie(
            labels=data['labels'],
            values=data['values'],
            hole=0.6,
            marker=dict(colors=colors_list),
            textinfo='percent',
            hoverinfo='label+percent'
        )],
        layout=go.Layout(
            title=dict(text="Répartition des évaluations", x=0.5),
            height=400,
            showlegend=True
        )
    )
    
    return fig

def create_notes_comparison_chart(user_id):
    """Crée un graphique comparatif des notes"""
    data_notes = get_notes_et_moyennes(user_id)
    
    if not data_notes:
        # Graphique vide si pas de données
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune note disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Comparaison de vos notes avec la moyenne de classe",
            height=400
        )
        return fig
    
    df = pd.DataFrame(data_notes)
    
    fig = go.Figure()
    
    # Barres pour les notes de l'étudiant
    fig.add_trace(go.Bar(
        name='Vos notes',
        x=df['Cours'],
        y=df['Notes'],
        marker_color='#4ECDC4'
    ))
    
    # Barres pour la moyenne de classe
    fig.add_trace(go.Bar(
        name='Moyenne classe',
        x=df['Cours'],
        y=df['Moyenne Classe'],
        marker_color='#FF6B6B'
    ))
    
    fig.update_layout(
        title='Comparaison de vos notes avec la moyenne de classe',
        xaxis_title='Cours',
        yaxis_title='Notes',
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

@login_required
def dashboard_etudiant(request):
    """Vue principale du dashboard étudiant"""
    if request.user.role != 'etudiant':
        return render(request, 'error.html', {
            'message': 'Accès non autorisé. Vous devez être étudiant pour accéder à ce dashboard.'
        })
    
    # Récupérer les informations de l'étudiant
    etudiant = get_etudiant_info(request.user.id)
    if not etudiant:
        return render(request, 'error.html', {
            'message': 'Étudiant non trouvé.'
        })
    
    # Récupérer les cours de la filière
    cours_filiere = get_cours_filiere(etudiant.get('filiere_id'))
    
    # Préparer les données des cours
    cours_data = []
    for cours in cours_filiere:
        ressources = get_ressources_cours(cours['cours_nom'])
        
        if cours['professeurs']:
            professeurs_noms = [f"{prof['prof_prenom']} {prof['prof_nom']}" for prof in cours['professeurs']]
            professeurs_emails = [prof['prof_email'] for prof in cours['professeurs']]
            professeur_str = "; ".join(professeurs_noms)
            email_str = "; ".join(professeurs_emails)
        else:
            professeur_str = "Non assigné"
            email_str = "Non disponible"
        
        cours_data.append({
            'nom': cours['cours_nom'],
            'professeurs': professeur_str,
            'emails': email_str,
            'ressources': ressources
        })
    
    # Récupérer les notes et calculer les moyennes
    data_notes = get_notes_et_moyennes(request.user.id)
    df_notes = pd.DataFrame(data_notes) if data_notes else pd.DataFrame()
    
    moyenne_generale_etudiant = round(df_notes['Notes'].mean(), 2) if not df_notes.empty else 0
    moyenne_generale_classe = round(df_notes['Moyenne Classe'].mean(), 2) if not df_notes.empty else 0
    
    # Créer les graphiques
    fig_evaluation = create_evaluation_charts(etudiant.get('filiere_id'))
    fig_notes = create_notes_comparison_chart(request.user.id)
    
    # Convertir les graphiques en HTML
    graph_evaluation_html = plot(fig_evaluation, output_type='div', include_plotlyjs=False)
    graph_notes_html = plot(fig_notes, output_type='div', include_plotlyjs=False)
    
    context = {
        'etudiant': etudiant,
        'cours_data': cours_data,
        'moyenne_generale_etudiant': moyenne_generale_etudiant,
        'moyenne_generale_classe': moyenne_generale_classe,
        'graph_evaluation': graph_evaluation_html,
        'graph_notes': graph_notes_html,
        'has_notes': not df_notes.empty
    }
    
    return render(request, 'dashboard_etudiant.html', context)

# API endpoints pour les données dynamiques (optionnel)
@login_required
def api_student_notes(request):
    """API pour récupérer les notes d'un étudiant"""
    if request.user.role != 'etudiant':
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    data_notes = get_notes_et_moyennes(request.user.id)
    return JsonResponse({'notes': data_notes})

@login_required  
def api_evaluation_modes(request):
    """API pour récupérer les modes d'évaluation"""
    if request.user.role != 'etudiant':
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    etudiant = get_etudiant_info(request.user.id)
    if not etudiant:
        return JsonResponse({'error': 'Étudiant non trouvé'}, status=404)
    
    data = get_modes_evaluation(etudiant.get('filiere_id'))
    return JsonResponse(data)
    
    return render(request, 'monapp/dashboard.html', context)

@login_required
def affectation_chef_filiere(request):
    if request.user.role != 'administrateur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    filieres = Filiere.objects.all().prefetch_related('utilisateurs', 'cours')
    filieres_sans_chef = []
    filieres_avec_chef = []

    for filiere in filieres:
        if filiere.chef:
            filieres_avec_chef.append(filiere)
        else:
            filieres_sans_chef.append(filiere)

    # Récupérer les chefs de filière existants
    chefs_filiere = Utilisateur.objects.filter(role='chef_filiere')

    # Récupérer tous les professeurs
    professeurs = Professeur.objects.all()

    context = {
        'filieres_sans_chef': filieres_sans_chef,
        'filieres_avec_chef': filieres_avec_chef,
        'chefs_filiere': chefs_filiere,
        'professeurs': professeurs,
        'total_filieres': filieres.count(),
    }
    return render(request, 'monapp/admin_dashboard.html', context)


@login_required
def affecter_chef(request):
    """
    Vue pour traiter l'affectation d'un chef à une filière
    """
    if request.method != 'POST':
        return redirect('monapp/admin_dashboard')
    
    # Vérifier que l'utilisateur est administrateur
    if request.user.role != 'administrateur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    filiere_id = request.POST.get('filiere_id')
    utilisateur_id = request.POST.get('utilisateur_id')
    
    if not filiere_id or not utilisateur_id:
        messages.error(request, 'Données manquantes pour l\'affectation.')
        return redirect('monapp/admin_dashboard')
    
    try:
        with transaction.atomic():
            # Récupérer la filière et l'utilisateur
            filiere = get_object_or_404(Filiere, id=filiere_id)
            utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
            
            # Vérifier que la filière n'a pas déjà un chef
            if filiere.chef:
                messages.warning(
                    request, 
                    f'La filière "{filiere.nom}" a déjà un chef de filière assigné.'
                )
                return redirect('affectation_chef_filiere')
            
            # Vérifier que l'utilisateur n'est pas déjà chef d'une autre filière
            if utilisateur.role == 'chef_filiere' and utilisateur.filiere:
                messages.warning(
                    request,
                    f'{utilisateur.get_full_name()} est déjà chef de la filière "{utilisateur.filiere.nom}".'
                )
                return redirect('affectation_chef_filiere')
            
            # Effectuer l'affectation
            utilisateur.role = 'chef_filiere'
            utilisateur.filiere = filiere
            utilisateur.save()
            
            messages.success(
                request,
                f'{utilisateur.get_full_name()} a été affecté comme chef de la filière "{filiere.nom}" avec succès.'
            )
            
    except Exception as e:
        messages.error(
            request,
            f'Erreur lors de l\'affectation : {str(e)}'
        )
    
    return redirect('monapp/admin_dashboard')

@login_required
def retirer_chef(request):
    """
    Vue pour retirer un chef de filière (optionnelle)
    """
    if request.method != 'POST':
        return redirect('monapp/admin_dashboard')
    
    # Vérifier que l'utilisateur est administrateur
    if request.user.role != 'administrateur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('dashboard')
    
    utilisateur_id = request.POST.get('utilisateur_id')
    
    if not utilisateur_id:
        messages.error(request, 'Utilisateur non spécifié.')
        return redirect('monapp/admin_dashboard')
    
    try:
        with transaction.atomic():
            utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
            
            if utilisateur.role != 'chef_filiere':
                messages.warning(request, 'Cet utilisateur n\'est pas chef de filière.')
                return redirect('affectation_chef_filiere')
            
            filiere_nom = utilisateur.filiere.nom if utilisateur.filiere else 'Inconnue'
            
            # Retirer le rôle de chef de filière
            utilisateur.role = 'etudiant'  # ou un autre rôle par défaut
            utilisateur.filiere = None
            utilisateur.save()
            
            messages.success(
                request,
                f'{utilisateur.get_full_name()} n\'est plus chef de la filière "{filiere_nom}".'
            )
            
    except Exception as e:
        messages.error(request, f'Erreur lors du retrait : {str(e)}')
    
    return redirect('monapp/admin_dashboard')

# API pour obtenir des statistiques en temps réel (optionnel)
@login_required
def get_affectation_stats(request):
    """
    API pour récupérer les statistiques d'affectation en JSON
    """
    if request.user.role != 'administrateur':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    filieres = Filiere.objects.all()
    filieres_sans_chef = [f for f in filieres if not f.chef]
    utilisateurs_disponibles = Utilisateur.objects.filter(
        role__in=['etudiant', 'administrateur']
    ).exclude(role='chef_filiere')
    
    return JsonResponse({
        'total_filieres': filieres.count(),
        'filieres_sans_chef': len(filieres_sans_chef),
        'utilisateurs_disponibles': utilisateurs_disponibles.count(),
        'filieres_avec_chef': filieres.count() - len(filieres_sans_chef)
    })

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

import re
@login_required
def modifier_chef(request):
    """
    Vue pour modifier l'affectation d'un chef de filière
    """
    if request.method != 'POST':
        return redirect('monapp/admin_dashboard')
    
    filiere_id = request.POST.get('filiere_id')
    utilisateur_id = request.POST.get('utilisateur_id')
    
    # Vérification des paramètres requis
    if not filiere_id:
        messages.error(request, "Filière non spécifiée.")
        return redirect('monapp/admin_dashboard')
    
    try:
        # Récupérer la filière
        from .models import Filiere  # Ajustez l'import selon votre structure
        filiere = get_object_or_404(Filiere, id=filiere_id)
        
        # Vérifier si un utilisateur existant est sélectionné
        if utilisateur_id:
            try:
                nouvel_utilisateur = User.objects.get(id=utilisateur_id)
                
                # Vérifier que l'utilisateur n'est pas déjà chef d'une autre filière
                if hasattr(nouvel_utilisateur, 'filiere_dirigee') and nouvel_utilisateur.filiere_dirigee != filiere:
                    messages.error(request, f"{nouvel_utilisateur.get_full_name()} est déjà chef d'une autre filière.")
                    return redirect('monapp/admin_dashboard')
                
                # Retirer l'ancien chef du groupe si il existe
                ancien_chef = filiere.chef
                if ancien_chef:
                    try:
                        chef_group = Group.objects.get(name='Chef de Filière')
                        ancien_chef.groups.remove(chef_group)
                    except Group.DoesNotExist:
                        pass
                
                # Affecter le nouveau chef
                filiere.chef = nouvel_utilisateur
                filiere.save()
                
                # Ajouter le nouveau chef au groupe
                try:
                    chef_group, created = Group.objects.get_or_create(name='Chef de Filière')
                    nouvel_utilisateur.groups.add(chef_group)
                except Exception as e:
                    messages.warning(request, f"Chef affecté mais erreur lors de l'ajout au groupe: {str(e)}")
                
                messages.success(request, f"Chef de filière modifié avec succès. {nouvel_utilisateur.get_full_name()} est maintenant chef de {filiere.nom}.")
                
            except User.DoesNotExist:
                messages.error(request, "Utilisateur sélectionné introuvable.")
                return redirect('monapp/admin_dashboard')
        
        # Sinon, créer un nouveau chef
        else:
            # Récupérer les données du nouveau chef
            first_name = request.POST.get('new_chef_first_name', '').strip()
            last_name = request.POST.get('new_chef_last_name', '').strip()
            username = request.POST.get('new_chef_username', '').strip()
            email = request.POST.get('new_chef_email', '').strip()
            password = request.POST.get('new_chef_password', '')
            confirm_password = request.POST.get('new_chef_confirm_password', '')
            
            # Validation des champs obligatoires
            if not all([first_name, last_name, username, email, password, confirm_password]):
                messages.error(request, "Tous les champs sont obligatoires pour créer un nouveau chef.")
                return redirect('monapp/admin_dashboard')
            
            # Validation du mot de passe
            if password != confirm_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect('monapp/admin_dashboard')
            
            # Validation de l'email
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                messages.error(request, "Format d'email invalide.")
                return redirect('monapp/admin_dashboard')
            
            # Validation du nom d'utilisateur
            if len(username) < 3:
                messages.error(request, "Le nom d'utilisateur doit contenir au moins 3 caractères.")
                return redirect('monapp/admin_dashboard')
            
            try:
                with transaction.atomic():
                    # Vérifier l'unicité du nom d'utilisateur et de l'email
                    if User.objects.filter(username=username).exists():
                        messages.error(request, f"Le nom d'utilisateur '{username}' existe déjà.")
                        return redirect('monapp/admin_dashboard')
                    
                    if User.objects.filter(email=email).exists():
                        messages.error(request, f"L'email '{email}' est déjà utilisé.")
                        return redirect('monapp/admin_dashboard')
                    
                    # Validation du mot de passe Django
                    try:
                        validate_password(password)
                    except ValidationError as e:
                        messages.error(request, f"Mot de passe invalide: {', '.join(e.messages)}")
                        return redirect('monapp/admin_dashboard')
                    
                    # Retirer l'ancien chef du groupe si il existe
                    ancien_chef = filiere.chef
                    if ancien_chef:
                        try:
                            chef_group = Group.objects.get(name='Chef de Filière')
                            ancien_chef.groups.remove(chef_group)
                        except Group.DoesNotExist:
                            pass
                    
                    # Créer le nouvel utilisateur
                    nouveau_chef = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name
                    )
                    
                    # Affecter le nouveau chef à la filière
                    filiere.chef = nouveau_chef
                    filiere.save()
                    
                    # Ajouter au groupe Chef de Filière
                    try:
                        chef_group, created = Group.objects.get_or_create(name='Chef de Filière')
                        nouveau_chef.groups.add(chef_group)
                    except Exception as e:
                        messages.warning(request, f"Chef créé et affecté mais erreur lors de l'ajout au groupe: {str(e)}")
                    
                    messages.success(request, f"Nouveau chef de filière créé et affecté avec succès. {nouveau_chef.get_full_name()} est maintenant chef de {filiere.nom}.")
                    
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du nouveau chef: {str(e)}")
                return redirect('monapp/admin_dashboard')
    
    except Exception as e:
        messages.error(request, f"Erreur lors de la modification du chef de filière: {str(e)}")
    
    return redirect('monapp/admin_dashboard')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import subprocess
import threading
import time
import requests

# Variable globale pour stocker le processus Dash
dash_process = None

def start_dash_app():
    """Démarre l'application Dash en arrière-plan"""
    global dash_process
    try:
        # Chemin vers votre fichier dashboard_admin.py
        dash_process = subprocess.Popen([
            'python', 'Dashadmin.py'
        ], cwd='C:/Users/Lenovo/Downloads/Tutoriel/mon_projet_django/appcours/Dashadmin.py')  # Remplacez par le chemin réel
        time.sleep(3)  # Attendre que l'app démarre
    except Exception as e:
        print(f"Erreur lors du démarrage de Dash: {e}")

@login_required
def dashboard_admin_view(request):
    """Vue pour afficher le dashboard administrateur"""
    global dash_process
    
    # Vérifier si l'utilisateur est admin
    if not request.user.is_staff:
        return render(request, 'error.html', {'message': 'Accès non autorisé'})
    
    # Démarrer l'app Dash si elle n'est pas déjà en cours
    if dash_process is None:
        thread = threading.Thread(target=start_dash_app)
        thread.daemon = True
        thread.start()
    
    # URL de l'application Dash
    dash_url = "http://127.0.0.1:8050"
    
    context = {
        'dash_url': dash_url,
        'user': request.user
    }
    
    return render(request, 'monapp/Dashadmin.html', context)

@login_required
def check_dash_status(request):
    """Vérifie si l'application Dash est en cours d'exécution"""
    try:
        response = requests.get("http://127.0.0.1:8050", timeout=5)
        if response.status_code == 200:
            return JsonResponse({'status': 'running'})
    except:
        pass
    
    return JsonResponse({'status': 'not_running'})

from django.http import HttpResponse
def start_dash_view(request):
    # Exemple simple
    return HttpResponse("Dash démarré !")

def dashboard_chef(request):
    """Vue pour afficher le dashboard du chef de filière"""
    return render(request, 'monapp/dashboard_chef.html')

@login_required
@require_http_methods(["POST"])
def modifier_chef(request):
    """
    View to modify the chef (head) of a filiere (department/program)
    """
    try:
        filiere_id = request.POST.get('filiere_id')
        
        if not filiere_id:
            messages.error(request, 'ID de filière manquant.')
            return redirect('affectation')
        
        # Get the filiere object
        filiere = get_object_or_404(Filiere, id=filiere_id)
        
        # Check if creating a new chef
        if request.POST.get('new_chef_first_name'):
            return create_new_chef_and_assign(request, filiere)
        
        # Check if assigning existing user
        utilisateur_id = request.POST.get('utilisateur_id')
        if utilisateur_id:
            return assign_existing_chef(request, filiere, utilisateur_id)
        
        messages.error(request, 'Aucune action valide sélectionnée.')
        return redirect('affectation')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la modification: {str(e)}')
        return redirect('affectation')


def create_new_chef_and_assign(request, filiere):
    """
    Create a new user and assign as chef de filiere
    """
    try:
        # Get form data
        first_name = request.POST.get('new_chef_first_name', '').strip()
        last_name = request.POST.get('new_chef_last_name', '').strip()
        username = request.POST.get('new_chef_username', '').strip()
        email = request.POST.get('new_chef_email', '').strip()
        password = request.POST.get('new_chef_password', '')
        confirm_password = request.POST.get('new_chef_confirm_password', '')
        
        # Validation
        if not all([first_name, last_name, username, email, password]):
            messages.error(request, 'Tous les champs sont obligatoires pour créer un nouveau chef.')
            return redirect('affectation')
        
        if password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return redirect('affectation')
        
        # Check if username already exists
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, f'Le nom d\'utilisateur "{username}" existe déjà.')
            return redirect('affectation')
        
        # Check if email already exists
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, f'L\'email "{email}" est déjà utilisé.')
            return redirect('affectation')
        
        # Create new user using your custom Utilisateur model
        new_user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='chef_filiere',  # Set role directly
            filiere=filiere  # Assign to filiere
        )
        
        # Use the custom chef setter
        filiere.chef = new_user
        
        messages.success(request, f'Nouveau chef "{first_name} {last_name}" créé et assigné à la filière "{filiere.nom}".')
        return redirect('affectation')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création du nouveau chef: {str(e)}')
        return redirect('affectation')


def assign_existing_chef(request, filiere, utilisateur_id):
    """
    Assign an existing user as chef de filiere
    """
    try:
        chef = None
        
        # Parse the utilisateur_id (could be "user-X" or "prof-X" format)
        if utilisateur_id.startswith('user-'):
            # It's a Utilisateur model
            user_id = utilisateur_id.replace('user-', '')
            chef = get_object_or_404(Utilisateur, id=user_id)
            
        elif utilisateur_id.startswith('prof-'):
            # It's a Professeur model - create a new Utilisateur from Professeur
            prof_id = utilisateur_id.replace('prof-', '')
            professeur = get_object_or_404(Professeur, id=prof_id)
            
            # Check if a Utilisateur with this email already exists
            existing_user = Utilisateur.objects.filter(email=professeur.email).first()
            if existing_user:
                chef = existing_user
            else:
                # Create new Utilisateur from Professeur data
                # Generate a username from the professor's name
                base_username = f"{professeur.prenom.lower()}.{professeur.nom.lower()}"
                username = base_username
                counter = 1
                while Utilisateur.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                chef = Utilisateur.objects.create_user(
                    username=username,
                    email=professeur.email,
                    password='temppassword123',  # You might want to generate a random password
                    first_name=professeur.prenom,
                    last_name=professeur.nom,
                    telephone=professeur.telephone,
                    role='chef_filiere',
                    filiere=filiere
                )
                
                messages.info(request, f'Compte utilisateur créé pour le professeur {professeur.prenom} {professeur.nom}. Mot de passe temporaire: temppassword123')
            
        else:
            # Regular user ID (without prefix)
            chef = get_object_or_404(Utilisateur, id=utilisateur_id)
        
        if not chef:
            messages.error(request, 'Utilisateur non trouvé.')
            return redirect('affectation')
        
        # Store previous chef info for message
        previous_chef = filiere.chef
        
        # Use the custom chef setter which handles role changes
        filiere.chef = chef
        
        if previous_chef:
            messages.success(
                request, 
                f'Chef de filière modifié: {previous_chef.first_name} {previous_chef.last_name} → {chef.first_name} {chef.last_name} pour la filière "{filiere.nom}".'
            )
        else:
            messages.success(
                request, 
                f'Chef de filière assigné: {chef.first_name} {chef.last_name} pour la filière "{filiere.nom}".'
            )
        
        return redirect('affectation')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'assignation: {str(e)}')
        return redirect('affectation')



@login_required
def affectation(request):
    """
    View for the affectation page
    """
    # Get filières without chef
    filieres_sans_chef = []
    for filiere in Filiere.objects.all():
        if filiere.chef is None:  # Using the property
            filieres_sans_chef.append(filiere)
    
    # Get filières with chef
    filieres_avec_chef = []
    for filiere in Filiere.objects.all():
        if filiere.chef is not None:  # Using the property
            filieres_avec_chef.append(filiere)
    
    # Get available users for chef assignment
    # Users who are not already chefs of other filières
    chefs_filiere = Utilisateur.objects.filter(role='chef_filiere')
    
    # Get users who could become chefs (excluding current chefs of other filières)
    utilisateurs_disponibles = Utilisateur.objects.filter(
        role__in=['etudiant', 'chef_filiere']
    ).exclude(
        id__in=[f.chef.id for f in filieres_avec_chef if f.chef]
    )
    
    # Get all professeurs
    professeurs = Professeur.objects.all()
    
    context = {
        'filieres_sans_chef': filieres_sans_chef,
        'filieres_avec_chef': filieres_avec_chef,
        'utilisateurs_disponibles': utilisateurs_disponibles,
        'chefs_filiere': chefs_filiere,
        'professeurs': professeurs,
    }
    
    return render(request, 'your_template_name.html', context)  # Replace with your actual template name