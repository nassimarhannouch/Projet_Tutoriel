from django.contrib import admin
from django.urls import path, include
from django.urls import path

from django.contrib.auth import views as auth_views
from appcours import views  # Assurez-vous que c'est bien 'monapp.views' si votre application s'appelle 'monapp'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/custom_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('', views.login_view, name='login'),
    path('register/', views.register_etudiant, name='register_etudiant'),
    path('etudiant/dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'),
    path('chef_filiere/dashboard/', views.chef_filiere_dashboard, name='chef_filiere_dashboard'),

    path('', views.home, name='home'),

    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='registration/reset_password.html'), name='password_reset'),

    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/reset_password_done.html'), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/reset_password_complete.html'), name='password_reset_complete'),

    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('confirm/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('feedback/', views.soumettre_feedback, name='soumettre_feedback'),
    # urls.py
    # urls.py
    path('merci_feedback/', views.merci_feedback, name='merci_feedback'),
    path('profil/', views.profil_etudiant, name='profil_etudiant'),
    path('home/', views.etudiant_dashboard, name='home'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/get_professeurs_by_cours/<int:cours_id>/', views.get_professeurs_by_cours, name='get_professeurs_by_cours'),
     # Nouvelle URL pour le dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # URL pour django-plotly-dash
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('chat_validation/', views.chat_validation, name='chat_validation'),
path('valider_feedback_serieux/', views.valider_feedback_serieux, name='valider_feedback_serieux'),
path('api/enregistrer_feedback_serieux/', views.enregistrer_feedback_serieux, name='enregistrer_feedback_serieux'),
path('affectation/', views.affectation_chef_filiere, name='affectation_chef_filiere'),
    path('affectation/', views.affectation_chef_filiere, name='affectation'),  # Alias
    path('affecter-chef/', views.affecter_chef, name='affecter_chef'),
    path('retirer-chef/', views.retirer_chef, name='retirer_chef'),
    path('api/affectation-stats/', views.get_affectation_stats, name='affectation_stats'),
    path('modifier-chef/', views.modifier_chef, name='modifier_chef'),
    path('Dashadmin/', views.dashboard_admin_view, name='Dashadmin'),
    path('check-dash-status/', views.check_dash_status, name='check_dash_status'),
    path('start-dash/', views.start_dash_view, name='start_dash'),
    path('dashboard-chef/', views.dashboard_chef, name='dashboard_chef'),
    path('affecter-chef/', views.affecter_chef, name='affecter_chef'),
path('modifier-chef/', views.modifier_chef, name='modifier_chef'),






    



]
