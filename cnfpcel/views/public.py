"""Pages publiques du site (accueil, articles, événements, formations, galerie, recherche)."""
from ._commun import *  # noqa: F401,F403

__all__ = ['index', 'detail_article', 'article_liste', 'evenement_detail', 'evenement_liste', 'personnel_liste', 'page_indisponible', 'list_formation', 'list_section_formation', 'galerie_index', 'recherche_index']


def index(request):
    personnel = Personnel.objects.filter(ne_pas_afficher=0)[:4]
    article = TitreArticle.objects.filter(statut=1).order_by('-date_de_publication')[:8]
    derniere_activite = TitreArticle.objects.filter(statut=1).order_by('-date_de_publication')[:1]
    formation = Formation.objects.filter(publiee=True).order_by('-id')[:8]
    now = timezone.now()
    evenement = Evenement.objects.filter(date__gt=now).order_by('date')[:3]

    domaine_formation = DomaineFormation.objects.all().order_by('-id')[:6]

    total_formation = Formation.objects.filter(publiee=True).count()
    
    form = MessageContactForm()
    info=0

    if request.method == 'POST':
        form = MessageContactForm(request.POST)
        if form.is_valid() :
            info = 1
            # Données sécurisées et validées
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            telephone = form.cleaned_data['telephone']
            message = form.cleaned_data['message']
            # Enregistrement dans la base de données
            contact_message = MessageContact(
                nom=nom,
                email=email,
                telephone=telephone,
                message=message,
                sujet="Message envoyé depuis l'accueil",
                lu=0
            )
            contact_message.save()
            messages.success(request,'Votre message a été envoyé avec succès.')
            return redirect('index')

    context = {
        'derniere_activite':derniere_activite,
        'personnel' : personnel,
        'article':article,
        'evenement':evenement,
        'domaine_formation':domaine_formation,
        'total_formation' : total_formation,
        'formation':formation,
        'form':form,
        'info':info,
    }
    return render(request,'accueil/index.html',context)


def detail_article(request,id):
    article = get_object_or_404(TitreArticle,id=id)
    paragraphe = Paragraphe.objects.filter(titreArticle=article)
    autre_actualite = TitreArticle.objects.filter(statut=1).order_by('-id')[:10]

    context={
        'article':article,
        'paragraphe':paragraphe,
        'autre_actualite':autre_actualite,
    }
    return render(request,'accueil/detail_article.html',context)


def article_liste(request):
    article = TitreArticle.objects.all().order_by('-id')
    return render(request,'accueil/article_liste.html',{'article':article})


def evenement_detail(request,id):
    evenement = get_object_or_404(Evenement,id=id)
    autre_evenement = Evenement.objects.all().order_by('-id')[:10]
    context={
        'evenement':evenement,
        'autre_evenement':autre_evenement,
    }
    return render(request,'accueil/evenement_detail.html',context)


def evenement_liste(request):
    evenement = Evenement.objects.all().order_by('-id')
    return render(request,'accueil/evenement_liste.html',{'evenement':evenement})


def personnel_liste(request):
    personnel = Personnel.objects.filter(ne_pas_afficher=0)
    return render(request,'accueil/personnel_liste.html',{'personnel':personnel})


def page_indisponible(request):
    return render(request,'accueil/page_indisponible.html')


def list_formation(request,id):
    if id==0:
        formation = Formation.objects.filter(publiee=True).order_by('-id')
        domaine = DomaineFormation.objects.none()

    else:
        domaine = get_object_or_404(DomaineFormation,id=id)
        formation = Formation.objects.filter(domaine=domaine, publiee=True).order_by('-id')
    context={
        'formation':formation,
        'domaine':domaine,
    }
    return render(request,'accueil/list_formation/list_formation.html',context)


def list_section_formation(request, id):
    formation = get_object_or_404(Formation, id=id)
    if not formation.publiee:
        # Formation en attente de validation : visible seulement par le personnel
        # et par les formateurs qui la dispensent (aperçu).
        from ..roles import est_personnel, formateur_de
        fo = formateur_de(request.user)
        if not (est_personnel(request.user)
                or (fo and formation.formation_dispenser.filter(formateur=fo).exists())):
            raise Http404("Formation non publiée")
    etudiant = None
    inscription = None
    info = ""
    erreur = ""
    evaluation = None
    
    if request.user.is_authenticated:
        etudiant = Etudiant.objects.filter(utilisateur=request.user).first()
        inscription = Inscription.objects.filter(etudiant=etudiant,formation=formation)
        evaluation = Evaluation.objects.filter(formation=formation)

        
    form = EtudiantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]

        etudiant_ajout, created = Etudiant.objects.get_or_create(
            email=email,
            defaults={
                "prenom": form.cleaned_data["prenom"],
                "nom": form.cleaned_data["nom"],
                "telephone": form.cleaned_data["telephone"],
            }
        )

        if not created:
            etudiant_ajout.prenom = form.cleaned_data["prenom"]
            etudiant_ajout.nom = form.cleaned_data["nom"]
            etudiant_ajout.telephone = form.cleaned_data["telephone"]
            etudiant_ajout.save()

        if Inscription.objects.filter(
            etudiant=etudiant_ajout,
            formation=formation
        ).exists():
            messages.error(
                request,
                "Vous êtes déjà inscrit à cette formation."
            )
            return redirect("list_section_formation", id)

        try:
            Inscription.objects.create(
                etudiant=etudiant_ajout,
                formation=formation
            )
        except IntegrityError:
            messages.error(
                request,
                "Vous êtes déjà inscrit·e à cette formation."
            )
            return redirect("list_section_formation", id)

        messages.success(
            request,
            "Votre inscription a été reçue. Nous vous tiendrons au courant de la prochaine étape."
        )

        message_html = render_to_string(
            "accueil/list_section_formation/info.html",
            {
                "etudiant": etudiant_ajout,
                "formation": formation,
                "logo_url" : request.build_absolute_uri(static('assets/img/logo1.png'))

            }
        )

        email_obj = EmailMultiAlternatives(
            subject=f"Inscription à la formation {formation.nom}",
            body=f"Votre inscription à la formation {formation.nom} a été reçue",
            from_email=email_reponse,
            to=[email]
        )
        email_obj.attach_alternative(message_html, "text/html")
        email_obj.send()

        return redirect("list_section_formation", id)
    
    context = {
        "etudiant": etudiant,
        "inscription":inscription,
        "form": form,
        "formation": formation,
        "evaluation" : evaluation,
        "info": info,
        "erreur": erreur,
    }

    return render(request,"accueil/list_section_formation/list_section_formation.html",context)


def galerie_index(request):
    galeries = Galerie.objects.prefetch_related("images").order_by("-date_prise")
    context = {
        'galeries':galeries
    }
    return render(request,'accueil/galerie_index.html',context)


def recherche_index(request):
    type_recherche = request.GET.get('type_recherche', '')
    terme_recherche = request.GET.get('terme_recherche', '')
    formations = Formation.objects.filter(
        Q(nom__icontains=terme_recherche) | Q(description__icontains=terme_recherche),
        publiee=True,
    ).order_by('-id')

    articles = TitreArticle.objects.filter(
        Q(titre__icontains=terme_recherche) | Q(date_de_publication__icontains=terme_recherche)
    ).order_by('-id')

    evenements = Evenement.objects.filter(
        Q(titre__icontains=terme_recherche) | Q(description__icontains=terme_recherche)
    ).order_by('-id')
    
    info = ""
    if type_recherche=='UNE FORMATION' and not formations.exists():
        info = "Aucun résultat trouvé pour votre recherche de formation. Veuillez essayer avec d'autres mots-clés."
    elif type_recherche=='UNE ACTUALITÉ / ÉVÈNEMENT' and not articles.exists() and not evenements.exists():
        info = "La recherche d'actualités/évènements n'est pas encore disponible. Veuillez essayer de rechercher une formation."
    else:
        info = 'AUCUN INFORMATION CORRESPONDANTE TROUVÉE.'
        
    context = {
        'formations': formations,
        'articles': articles,
        'evenements': evenements,
        'type_recherche': type_recherche,
        'info':info,
    }

    return render(request, 'accueil/list_formation/formation_recherche_index.html',context)
