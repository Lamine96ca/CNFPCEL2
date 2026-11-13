from django import forms
from .models import *
from django.utils import timezone

class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = ['prenom', 'nom', 'telephone', 'email', 'fonc', 'bio', 'photo','ne_pas_afficher']
        error_messages = {
            'prenom': {
                'required': "Le prénom est obligatoire."
            },
            'email': {
                'invalid': "Adresse email invalide.",
                'required': "L’email est requis pour créer le compte utilisateur."
            },
            'photo': {
                'invalid': "Le fichier n’est pas une image valide."
            }
        }
        widgets = {
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '*'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '*'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '*'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '*'
            }),
            'fonc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': ''
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'ne_pas_afficher': forms.CheckboxInput(attrs={
                'required':False,
                'classe':'form-check-input',
            }),
           
           
        }


    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and photo.size > 1 * 1024 * 1024:  # 1 Mo
            raise forms.ValidationError("L’image ne doit pas dépasser 1Mo.")
        return photo
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Personnel.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre personnel.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        qs = Personnel.objects.filter(telephone=telephone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà enregistré.")
        return telephone

class TitreArticleForm(forms.ModelForm):
    class Meta:
        model = TitreArticle
        fields = ['titre','date_de_publication','statut']
        widgets = {
            'titre':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':"Entrer le titre de l'article",
            }),
            'date_de_publication':forms.DateTimeInput(attrs={
                'class':'form-control',
                'type':'datetime-local',
            }),
            'statut':forms.CheckboxInput(attrs={
                'classe':'form-check-input',
            }),
        }

class ParagrapheForm(forms.ModelForm):
    class Meta:
        model = Paragraphe
        fields = ['contenu','image']
        widgets = {
            'contenu':forms.Textarea(attrs={
                'class':'form-control',
                'row':5,
                'placeholder':'Tapez contenu ici!'
            }),
            'image':forms.ClearableFileInput(attrs={
                'class':'form-control'
            })
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size == 1* 1024*1024:
            raise forms.ValidationError("L'image ne doit pas depasser 1Mo.")
        return image

class MessageContactForm(forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'telephone', 'message']
        error_messages = {
            'nom': {
                'required': "Le nom est obligatoire."
            },
            'email': {
                'invalid': "Adresse email invalide.",
                'required': "L’email est requis."
            },
            'sujet': {
                'required': "Le sujet est obligatoire."
            },
            'message': {
                'required': "Le message ne peut pas être vide."
            }
        }

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['titre', 'description', 'date', 'lieu', 'image']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "*"
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "*"
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "*"
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 1 * 1024 * 1024:  # 1 Mo
            raise forms.ValidationError("L’image ne doit pas dépasser 1Mo.")
        return image
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("La date de l'événement ne peut pas être dans le passé.")
        return date

class DomaineFormationForm(forms.ModelForm):
    class Meta:
        model = DomaineFormation
        fields = ['nom', 'description', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom du domaine de formation"
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "Description du domaine de formation"
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 1 * 1024 * 1024:  # 1 Mo
            raise forms.ValidationError("L’image ne doit pas dépasser 1Mo.")
        return image
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if nom == "":
            raise forms.ValidationError("Le nom du domaine est obligatoire.")
        else :
            qs = DomaineFormation.objects.filter(nom=nom)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ce domaine de formation existe déjà.")
        return nom
    

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['domaine', 'nom','duree', 'prix', 'description','image', 'video']
        widgets = {
            'domaine': forms.Select(attrs={
                'class': 'form-select'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "*"
            }),
            'duree': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "*"
            }),

            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': "Prix"
            }),
            
            
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "*"
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 1 * 1024 * 1024:  # 1 Mo
            raise forms.ValidationError("L’image ne doit pas dépasser 1Mo.")
        return image
    
    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and video.size > 20 * 1024 * 1024 :
            raise forms.ValidationError("La video ne doit pas dépasser 20Mo")
        return video
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if nom == "":
            raise forms.ValidationError("Le nom de la formation est obligatoire.")
        else :
            qs = Formation.objects.filter(nom=nom)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Cette formation existe déjà.")
        return nom

class SectionFormationForm(forms.ModelForm):
    class Meta:
        model = SectionFormation
        fields = ['titre', 'contenu']
        widgets = {

            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Titre de la section"
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "Contenu de la section"
            }),
        }

    
    def clean_titre(self):
        titre = self.cleaned_data.get('titre')
        formation = self.cleaned_data.get('formation')
        if titre == "":
            raise forms.ValidationError("Le titre de la section est obligatoire.")
        else : 
            qs = SectionFormation.objects.filter(titre=titre, formation=formation)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Une section avec ce titre existe déjà.")
        return titre
    
    def clean_contenu(self):
        contenu = self.cleaned_data.get('contenu')
        if contenu == "":
            raise forms.ValidationError("Le contenu de la section ne peut pas être vide.")
        return contenu 


class EtudiantForm(forms.ModelForm):
    class Meta: 
        model = Etudiant
        fields = ['prenom', 'nom', 'telephone', 'email']
        widgets = {
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Prénoms"
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom"
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Téléphone"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "E-mail"
            }),
        }

    def clean_prenom(self):
        prenom = self.cleaned_data.get('prenom')
        if not prenom:
            raise forms.ValidationError("Le prénom est obligatoire.")
        return prenom

    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if not nom:
            raise forms.ValidationError("Le nom est obligatoire.")
        return nom

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("L'email est obligatoire.")
        return email

class RessourceFormationForm(forms.ModelForm):
    class Meta:
        model = RessourceFormation
        fields = ['titre', 'pdf', 'video']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Titre"
            }),

            'pdf': forms.ClearableFileInput(attrs={  # Correction ici : dfp -> pdf
                'class': 'form-control',
                'placeholder': "Fichier .pdf",
                'accept': 'application/pdf'
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': "Vidéo",
                'accept': 'video/*'
            })
        }

    def clean_titre(self):
        titre = self.cleaned_data.get('titre')
        if titre == '':
            raise forms.ValidationError('Le titre est obligatoire')
        else:
            formation = self.cleaned_data.get('formation')
            qs = RessourceFormation.objects.filter(titre=titre, formation__nom=formation)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ce titre pour cette formation existe déjà.")
        return titre

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')
        if pdf and pdf.size > 1 * 1024 * 1024:
            raise forms.ValidationError("Le PDF ne doit pas dépasser 1Mo")
        return pdf

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and video.size > 100 * 1024 * 1024:
            raise forms.ValidationError("La vidéo ne doit pas dépasser 80Mo")
        return video


from django.forms.widgets import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

class GalerieForm(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Description de la galerie"
            }
        )
    )

    date_prise = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control"
            }
        )
    )

    images = forms.ImageField(
        widget=MultipleFileInput(
            attrs={
                "class": "form-control",
                "multiple": True,
                "accept": "image/*"
            }
        ),
        required=False
    )


#EVALUATION
class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['titre', 'formation', 'description', 'note_minimale', 'duree', 'actif']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'formation': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'note_minimale': forms.NumberInput(attrs={'class': 'form-control'}),
            'duree': forms.NumberInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    # 🔹 Validation personnalisée du titre
    def clean_titre(self):
        titre = self.cleaned_data.get('titre', '').strip()

        if not titre:
            raise forms.ValidationError("Le titre de l'évaluation est obligatoire.")

        # Vérifie qu'il n'y a pas déjà un test avec le même titre pour cette formation
        formation = self.cleaned_data.get('formation')
        if formation and Evaluation.objects.filter(titre__iexact=titre, formation=formation).exists():
            raise forms.ValidationError(
                "Une évaluation avec ce titre existe déjà pour cette formation."
            )

        return titre

#QUESTTION
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['texte']
        widgets = {
            'texte': forms.Textarea(attrs={'class': 'form-control', 'ROW':'4'}),
        }

    # 🔹 Validation personnalisée du titre
    def clean_texte(self):
        texte = self.cleaned_data.get('texte', '').strip()

        if not texte:
            raise forms.ValidationError("Le texte de la question est obligatoire.")

        # Vérifie qu'il n'y a pas déjà un test avec le même texte pour cette formation
        evaluation = self.cleaned_data.get('evaluation')
        if evaluation and Question.objects.filter(texte__iexact=texte, evaluation=evaluation).exists():
            raise forms.ValidationError(
                "Une question avec ce texte existe déjà pour cette évaluation."
            )

        return texte

#REPONSE
class ReponseForm(forms.ModelForm):
    class Meta:
        model = Reponse
        fields = [
            
            'texte',
            'correcte',
        ]
        widgets = {
            'texte': forms.Textarea(attrs={'class': 'form-control', 'row':'3'}),
            'correcte': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_texte(self):
        texte = self.cleaned_data.get('texte', '').strip()

        if not texte:
            raise forms.ValidationError("Le texte de la reponse est obligatoire.")

        # Vérifie qu'il n'y a pas déjà un test avec le même texte pour cette formation
        question = self.cleaned_data.get('question')
        if question and Reponse.objects.filter(texte__iexact=texte, question=question).exists():
            raise forms.ValidationError(
                "Une reponse avec ce texte existe déjà pour cette question."
            )

        return texte


class FormateurForm(forms.ModelForm):
    class Meta:
        model = Formateur
        fields = ['prenom', 'nom', 'telephone', 'email', 'bio']
        error_messages = {
            'prenom': {
                'required': "Le prénom est obligatoire."
            },
            'email': {
                'invalid': "Adresse email invalide.",
                'required': "L’email est requis pour créer le compte utilisateur."
            },
        }
        widgets = {
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du personnel'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du personnel'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de téléphone'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@institution.gov.gn'
            }),

            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brève biographie ou présentation'
            }),          
           
        }



    
    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise forms.ValidationError("L’email est requis pour créer le compte utilisateur.")
        qs = Formateur.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre formateur.")
        # Le compte de connexion utilise l'email comme identifiant
        comptes = User.objects.filter(username__iexact=email)
        if self.instance.pk and self.instance.utilisateur_id:
            comptes = comptes.exclude(pk=self.instance.utilisateur_id)
        if comptes.exists():
            raise forms.ValidationError("Un compte utilisateur existe déjà avec cet email.")
        return email

    def clean_telephone(self):
        telephone = (self.cleaned_data.get('telephone') or '').strip()
        qs = Formateur.objects.filter(telephone=telephone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà enregistré.")
        return telephone


class FormateurFormationsForm(forms.Form):
    """Choix des formations dispensées par un formateur."""
    formations = forms.ModelMultipleChoiceField(
        queryset=Formation.objects.order_by('nom'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Formations dispensées",
    )


class FormateurProfilForm(forms.ModelForm):
    """Informations modifiables par le formateur lui-même."""
    class Meta:
        model = Formateur
        fields = ['telephone', 'bio']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                         'placeholder': 'Présentez-vous en quelques lignes'}),
        }

    def clean_telephone(self):
        telephone = (self.cleaned_data.get('telephone') or '').strip()
        if Formateur.objects.filter(telephone=telephone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà enregistré.")
        return telephone


class EvaluationFormateurForm(forms.ModelForm):
    """Évaluation créée par un formateur : la formation est fixée par la page."""
    class Meta:
        model = Evaluation
        fields = ['titre', 'description', 'duree', 'note_minimale', 'actif']
        labels = {'duree': 'Durée (minutes)', 'note_minimale': 'Note minimale (%)', 'actif': 'Visible par les participants'}
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duree': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'note_minimale': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, formation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.formation = formation

    def clean_titre(self):
        titre = (self.cleaned_data.get('titre') or '').strip()
        if not titre:
            raise forms.ValidationError("Le titre de l'évaluation est obligatoire.")
        qs = Evaluation.objects.filter(titre__iexact=titre, formation=self.formation)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Une évaluation avec ce titre existe déjà pour cette formation.")
        return titre

    def clean_note_minimale(self):
        note = self.cleaned_data.get('note_minimale')
        if note is not None and note > 100:
            raise forms.ValidationError("La note minimale ne peut pas dépasser 100 %.")
        return note


class FormationFormateurForm(FormationForm):
    """Formation proposée ou modifiée par un formateur (le prix reste géré par l'administration)."""
    class Meta(FormationForm.Meta):
        fields = ['domaine', 'nom', 'duree', 'description', 'image', 'video']
        labels = {'domaine': 'Domaine', 'nom': 'Intitulé de la formation', 'duree': 'Durée',
                  'description': 'Description', 'image': 'Image de couverture (1 Mo max.)',
                  'video': 'Vidéo de présentation (20 Mo max.)'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['domaine'].empty_label = "— Choisir un domaine —"
        self.fields['nom'].widget.attrs['placeholder'] = "Ex. : Gestion budgétaire des communes"
        self.fields['duree'].widget.attrs['placeholder'] = "Ex. : 5 jours"
        self.fields['description'].widget.attrs['placeholder'] = "Objectifs, public visé, contenu…"
