from django.contrib import admin
from .models import (
    Utilisateur,
    Filiere,
    Promotion,
    Cours,
    Professeur,
    Feedback,
    CourseResource,
    Notes,
    ModeEvaluation,
)

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'filiere', 'promotion')
    list_filter = ('role', 'filiere', 'promotion')
    search_fields = ('username', 'email')

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'chef', 'nombre_etudiants')
    search_fields = ('nom',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('nom', 'annee_debut', 'annee_fin')
    search_fields = ('nom',)

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'filiere', 'note_moyenne')
    list_filter = ('filiere',)
    search_fields = ('nom',)

@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'email', 'telephone')
    search_fields = ('prenom', 'nom', 'email')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('cours', 'professeur', 'etudiant', 'note', 'date_creation', 'sentiment', 'anonyme', 'partager')
    list_filter = ('sentiment', 'date_creation', 'anonyme', 'partager')
    search_fields = ('cours__nom', 'professeur__nom', 'etudiant__username')

@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ('description', 'course_name', 'resource_link')
    search_fields = ('course_name', 'description')

@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'cours', 'note', 'date_creation')
    search_fields = ('etudiant__username', 'cours__nom')
    list_filter = ('cours',)

@admin.register(ModeEvaluation)
class ModeEvaluationAdmin(admin.ModelAdmin):
    list_display = ('mode', 'pourcentage', 'cours')
    list_filter = ('cours',)
    search_fields = ('mode', 'cours__nom')
