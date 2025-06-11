from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['cours','note', 'commentaire']
        widgets = {
            'cours': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Entrez votre feedback ici...'}),
        }