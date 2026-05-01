from django import forms
from .models import IdeaSubmission, INDUSTRY_CHOICES


class IdeaForm(forms.ModelForm):
    class Meta:
        model = IdeaSubmission
        fields = ['title', 'description', 'audience', 'industry']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Airbnb for study spaces',
                'maxlength': 80,
                'class': 'form-input',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your startup idea in detail. What problem does it solve? How does it work? Who is it for? (minimum 30 characters)',
                'rows': 6,
                'maxlength': 1500,
                'minlength': 30,
                'class': 'form-textarea',
                'id': 'id_description',
            }),
            'audience': forms.TextInput(attrs={
                'placeholder': 'e.g. College students aged 18-25',
                'maxlength': 200,
                'class': 'form-input',
            }),
            'industry': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description', '')
        if len(desc.strip()) < 30:
            raise forms.ValidationError("Please describe your idea in at least 30 characters.")
        return desc
