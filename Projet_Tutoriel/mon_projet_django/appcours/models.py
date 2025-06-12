from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.TextChoices):
    ETUDIANT = 'ETUDIANT', 'Étudiant'
    CHEF_FILIERE = 'CHEF_FILIERE', 'Chef de filière'
    ADMIN = 'ADMIN', 'Administrateur'
    PROF = 'PROF', 'Professeur'
# Modèle pour les utilisateurs

# Modèle pour les utilisateurs
class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    ROLES = (
        ('etudiant', 'Étudiant'),
        ('chef_filiere', 'Chef de Filière'),
        ('administrateur', 'Administrateur'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='etudiant')
    filiere = models.ForeignKey('Filiere', on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    promotion = models.ForeignKey('Promotion', on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Modèle pour les filières
class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

    @property
    def chef(self):
        """Retourne le chef de filière associé à cette filière."""
        return self.utilisateurs.filter(role='chef_filiere').first()

    @chef.setter
    def chef(self, utilisateur):
        """Définit le chef de cette filière."""
        # Retirer l'ancien chef
        anciens_chefs = self.utilisateurs.filter(role='chef_filiere')
        for ancien in anciens_chefs:
            ancien.role = 'etudiant'
            ancien.save()
        
        # Définir le nouvel utilisateur comme chef
        utilisateur.role = 'chef_filiere'
        utilisateur.filiere = self
        utilisateur.save()
    
    @property
    def nombre_etudiants(self):
        """Retourne le nombre d'étudiants dans cette filière."""
        return self.utilisateurs.filter(role='etudiant').count()

# Modèle pour les promotions
class Promotion(models.Model):
    nom = models.CharField(max_length=100)
    annee_debut = models.IntegerField(null=True, blank=True)
    annee_fin = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.nom

# Modèle pour les cours
class Cours(models.Model):
    nom = models.CharField(max_length=100)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='cours')
    
    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
    
    def __str__(self):
        return f"{self.nom} ({self.filiere.nom})"
    
    @property
    def note_moyenne(self):
        """Calcule la note moyenne du cours."""
        feedbacks = self.feedbacks.all()
        if not feedbacks:
            return None
        return sum(f.note for f in feedbacks) / feedbacks.count()

class Professeur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    cours = models.ManyToManyField(Cours, related_name='professeurs')
    
    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def cours_enseignes(self):
        """Retourne la liste des cours enseignés par ce professeur."""
        return self.cours.all()
    
    @property
    def note_moyenne(self):
        """Calcule la note moyenne du professeur à partir des feedbacks de tous ses cours."""
        feedbacks = Feedback.objects.filter(cours__in=self.cours.all())
        if not feedbacks.exists():
            return None
        return feedbacks.aggregate(models.Avg('note'))['note__avg']


# Modèle pour les feedbacks
class Feedback(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='feedbacks')
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, null=True, blank=True, related_name='feedbacks')
    etudiant = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    note = models.IntegerField()
    commentaire = models.TextField()
    suggestions = models.TextField(blank=True, null=True)
    date_cours = models.DateField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('positif', 'Positif'),
        ('neutre', 'Neutre'),
        ('négatif', 'Négatif')
    ])
    anonyme = models.BooleanField(default=False)
    partager = models.BooleanField(default=False)
    theme_pred = models.CharField(max_length=100, blank=True, null=True)  # thème prédit
    recommendations = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-date_creation']
    
    def __str__(self):
        cours_nom = self.cours.nom if self.cours else "Cours inconnu"
        etudiant_str = "Anonyme" if self.anonyme else (self.etudiant.username if self.etudiant else "Inconnu")
        return f"Feedback #{self.id} - {cours_nom} par {etudiant_str}"
    
from django.db import models

class CourseResource(models.Model):
    """Modèle pour les ressources de cours"""
    course_name = models.CharField(max_length=100)
    resource_link = models.URLField()
    description = models.TextField()
    
    def __str__(self):
        return f"{self.description} ({self.course_name})"

class Notes(models.Model):
    """Modèle pour les notes des étudiants"""
    etudiant = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='notes')
    cours = models.ForeignKey('Cours', on_delete=models.CASCADE, related_name='notes')
    note = models.DecimalField(max_digits=4, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        unique_together = ('etudiant', 'cours')
    
    def __str__(self):
        return f"Note de {self.etudiant.username} pour {self.cours.nom}: {self.note}/20"

class ModeEvaluation(models.Model):
    """Modèle pour les modes d'évaluation des cours"""
    cours = models.ForeignKey('Cours', on_delete=models.CASCADE, related_name='modes_evaluation')
    mode = models.CharField(max_length=100)  # Examen, Projet, TP, etc.
    pourcentage = models.IntegerField()  # Pourcentage de la note finale
    
    class Meta:
        verbose_name = "Mode d'évaluation"
        verbose_name_plural = "Modes d'évaluation"
    
    def __str__(self):
        return f"{self.mode} ({self.pourcentage}%) - {self.cours.nom}"
    