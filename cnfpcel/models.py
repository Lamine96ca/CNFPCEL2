from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Personnel(models.Model):
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    telephone = models.CharField(max_length=25, unique=True, verbose_name="Téléphone")
    email = models.CharField(max_length=150, unique=True, verbose_name="E-mail")
    fonc = models.CharField(max_length=100, verbose_name="Fonction")
    bio = models.CharField(max_length=200,blank=True,null=True, verbose_name="Biographie")
    photo = models.ImageField(upload_to="personnel/photo", default="personnel/photo/default.jpg")
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_personnel')
    ne_pas_afficher = models.BooleanField(default=0)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class TitreArticle(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre de l'article")
    date_de_publication = models.DateTimeField(verbose_name="Date")
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.titre

class Paragraphe(models.Model):
    titreArticle = models.ForeignKey(TitreArticle, on_delete=models.CASCADE, verbose_name="Titre de l'article",related_name='titre_paragraphe' )
    contenu = models.TextField(verbose_name="Contenu")
    image = models.ImageField(upload_to='article/paragraphe/', null=True, blank=True)

    def __str__(self):
         return f"Paragraphe {self.contenu} de {self.titreArticle}"

class MessageContact(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(max_length=150, verbose_name="E-mail")
    telephone = models.CharField(max_length=25, verbose_name="Téléphone")
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    lu = models.BooleanField(default=False, verbose_name="Lu")

    def __str__(self):
        return f"Message de {self.nom} - {self.sujet}"

class Evenement(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre de l'événement")
    description = models.TextField(verbose_name="Description de l'événement")
    date = models.DateField(verbose_name="Date de l'événement")
    lieu = models.CharField(max_length=200, verbose_name="Lieu de l'événement")
    image = models.ImageField(upload_to='evenements/', null=True, blank=True)

    def __str__(self):
        return self.titre

class DomaineFormation(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du domaine de formation")
    description = models.TextField(verbose_name="Description du domaine de formation")
    image = models.ImageField(upload_to='domaine_formation/', null=True, blank=True)

    def __str__(self):
        return self.nom

class Formation(models.Model):
    domaine = models.ForeignKey(DomaineFormation, on_delete=models.CASCADE, 
                                related_name='formations', 
                                verbose_name="Domaine de formation",
                                blank=True, null=True
                                )
    nom = models.CharField(max_length=100, verbose_name="Nom de la formation")
    description = models.TextField(verbose_name="Description de la formation")
    duree = models.CharField(max_length=50, verbose_name="Durée de la formation")
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de la formation", default=0)
    image = models.ImageField(upload_to='formations/', null=True, blank=True)
    video = models.FileField(upload_to='formations/videos/',blank=True, null=True)
    active = models.BooleanField(default=True, verbose_name="Inscriptions ouvertes")
    # Une formation proposée par un formateur reste invisible sur le site
    # tant que l'administration ne l'a pas publiée.
    publiee = models.BooleanField(default=True, verbose_name="Publiée sur le site")
    cree_par = models.ForeignKey('Formateur', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='formations_proposees', verbose_name="Proposée par")

    def __str__(self):
        return self.nom

class SectionFormation(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, 
                                  related_name='sections', 
                                  verbose_name="Formation"
                                  )
    titre = models.CharField(max_length=200, verbose_name="Titre de la section")
    contenu = models.TextField(verbose_name="Contenu de la section")

    def __str__(self):
        return f"{self.titre} - {self.formation.nom}"


class Etudiant(models.Model):
    prenom = models.CharField(max_length=100, verbose_name='Prénoms')
    nom = models.CharField(max_length=50, verbose_name='Nom')
    telephone = models.CharField(max_length=30, verbose_name='Téléphone', default="")
    email = models.CharField(max_length=100, verbose_name='E-mail')
    accept = models.BooleanField(verbose_name='Accepté', default=False)

    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_etudiant', blank=True, null=True)

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"

    
class Inscription(models.Model) : 
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    accepte = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        return f"{self.etudiant.prenom} {self.etudiant.nom} - {self.formation.nom}"

class RessourceFormation(models.Model) :
    titre = models.CharField(max_length=100, verbose_name='Titre')
    description = models.TextField(verbose_name='Description', default="")
    pdf = models.FileField(upload_to='formation/pfe/',verbose_name='Fichier pdf', blank=True, null=True)
    video = models.FileField(upload_to='formation/video_complet', verbose_name='Video', blank=True,null=True)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)

    class Meta :
        unique_together=('titre','formation')
    
    def __str__(self):
        return self.titre


class Galerie(models.Model):
    description = models.TextField()
    date_prise = models.DateField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description[:30]

class GalerieImage(models.Model):
    galerie = models.ForeignKey(
        Galerie,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="galerie/", verbose_name='Photo', blank=True, null=True)

    def __str__(self):
        return f"Image {self.id}"


#EVALUATION 
class Evaluation(models.Model):
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    note_minimale = models.PositiveIntegerField(default=70)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.titre
 
class Question(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    texte = models.TextField()

    def __str__(self):
        return self.texte[:50]

class Reponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    texte = models.CharField(max_length=255)
    correcte = models.BooleanField(default=False)

class Tentative(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    score = models.FloatField()
    reussi = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('etudiant', 'evaluation')

class ResultatEvaluation(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    score = models.FloatField()
    bonnes_reponses = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    reussi = models.BooleanField(default=False)
    date_passage = models.DateTimeField(auto_now_add=True)
    temps_ecoule = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.etudiant.prenom} {self.etudiant.nom} - {self.evaluation} ({self.score}%)"

class Formateur(models.Model):
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    telephone = models.CharField(max_length=25, unique=True, verbose_name="Téléphone")
    email = models.CharField(max_length=150, unique=True, verbose_name="E-mail")
    bio = models.CharField(max_length=200,blank=True,null=True, verbose_name="Biographie")
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_formateur', blank=True, null=True)
    def __str__(self):
        return f"{self.prenom} {self.nom}"

class DispenseFormation(models.Model):
    dateajout = models.DateField(auto_now_add=True)
    formateur = models.ForeignKey(Formateur,on_delete=models.CASCADE, related_name='formateur_dispenser')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='formation_dispenser')

    def __str__(self):
        return f"{self.formateur.prenom} {self.formateur.nom} - {self.formation.nom}"
