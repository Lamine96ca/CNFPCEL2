"""
Gestion des formateurs (côté personnel).

L'accès est réservé au personnel par `roles.AccesMiddleware`.
"""
import secrets
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from ..forms import FormateurForm, FormateurFormationsForm
from ..models import DispenseFormation, Formateur, Formation, Personnel

DOMAINE = settings.URL_PUBLIQUE
EMAIL_REPONSE = settings.DEFAULT_FROM_EMAIL


def _mot_de_passe(longueur=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(longueur))


def _envoyer_acces(request, formateur, mot_de_passe):
    """Envoie les identifiants au formateur. Retourne True si l'e-mail est parti."""
    try:
        html = render_to_string('gestion/formateur/email_acces.html', {
            'formateur': formateur, 'mot_de_passe': mot_de_passe, 'domaine': DOMAINE,
        })
        mail = EmailMultiAlternatives(
            subject='CNFPATEL - Accès à votre espace formateur',
            body=f"Identifiant : {formateur.email}\nMot de passe provisoire : {mot_de_passe}",
            from_email=EMAIL_REPONSE, to=[formateur.email],
        )
        mail.attach_alternative(html, 'text/html')
        mail.send()
        return True
    except Exception:
        return False


def _signaler_acces(request, formateur, mot_de_passe):
    if _envoyer_acces(request, formateur, mot_de_passe):
        messages.success(request, f"Les identifiants ont été envoyés à {formateur.email}.")
    else:
        messages.warning(
            request,
            f"L'e-mail n'a pas pu être envoyé. Transmettez ces accès au formateur : "
            f"identifiant {formateur.email} · mot de passe provisoire {mot_de_passe}",
        )


def _synchroniser_formations(formateur, formations):
    voulues = {f.id for f in formations}
    actuelles = set(formateur.formateur_dispenser.values_list('formation_id', flat=True))
    DispenseFormation.objects.filter(formateur=formateur, formation_id__in=actuelles - voulues).delete()
    DispenseFormation.objects.bulk_create(
        [DispenseFormation(formateur=formateur, formation_id=fid) for fid in voulues - actuelles]
    )


def formateur(request):
    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    recherche = request.GET.get('q', '').strip()

    formateurs = (Formateur.objects
                  .select_related('utilisateur')
                  .prefetch_related(Prefetch('formateur_dispenser',
                                             queryset=DispenseFormation.objects.select_related('formation')))
                  .annotate(nb_formations=Count('formateur_dispenser'))
                  .order_by('nom', 'prenom'))
    if recherche:
        formateurs = formateurs.filter(Q(nom__icontains=recherche) | Q(prenom__icontains=recherche)
                                       | Q(email__icontains=recherche) | Q(telephone__icontains=recherche))

    form = FormateurForm()
    form_formations = FormateurFormationsForm()
    show_modal = False

    if request.method == 'POST':
        form = FormateurForm(request.POST)
        form_formations = FormateurFormationsForm(request.POST)
        if form.is_valid() and form_formations.is_valid():
            mot_de_passe = _mot_de_passe()
            with transaction.atomic():
                nouveau = form.save(commit=False)
                compte = User.objects.create_user(
                    username=nouveau.email, email=nouveau.email, password=mot_de_passe,
                    first_name=nouveau.prenom, last_name=nouveau.nom,
                )
                nouveau.utilisateur = compte
                nouveau.save()
                _synchroniser_formations(nouveau, form_formations.cleaned_data['formations'])
            messages.success(request, f"Le formateur {nouveau} a été ajouté.")
            _signaler_acces(request, nouveau, mot_de_passe)
            return redirect('formateur')
        show_modal = True

    return render(request, 'gestion/formateur/formateur.html', {
        'active': 'formateur',
        'utilisateur': utilisateur,
        'formateurs': formateurs,
        'recherche': recherche,
        'form': form,
        'form_formations': form_formations,
        'show_modal': show_modal,
        'total_formations': Formation.objects.count(),
    })


def formateur_edit(request, id):
    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    fiche = get_object_or_404(Formateur, id=id)
    initiales = {'formations': Formation.objects.filter(formation_dispenser__formateur=fiche)}

    if request.method == 'POST':
        form = FormateurForm(request.POST, instance=fiche)
        form_formations = FormateurFormationsForm(request.POST)
        if form.is_valid() and form_formations.is_valid():
            with transaction.atomic():
                fiche = form.save()
                if fiche.utilisateur:
                    compte = fiche.utilisateur
                    compte.username = fiche.email
                    compte.email = fiche.email
                    compte.first_name = fiche.prenom
                    compte.last_name = fiche.nom
                    compte.save()
                _synchroniser_formations(fiche, form_formations.cleaned_data['formations'])
            messages.success(request, "Les informations du formateur ont été mises à jour.")
            return redirect('formateur')
    else:
        form = FormateurForm(instance=fiche)
        form_formations = FormateurFormationsForm(initial=initiales)

    return render(request, 'gestion/formateur/formateur_edit.html', {
        'active': 'formateur',
        'utilisateur': utilisateur,
        'fiche': fiche,
        'form': form,
        'form_formations': form_formations,
    })


@require_POST
def formateur_delete(request, id):
    fiche = get_object_or_404(Formateur, id=id)
    nom = str(fiche)
    with transaction.atomic():
        compte = fiche.utilisateur
        fiche.delete()
        # Le compte n'est supprimé que s'il ne sert à rien d'autre
        if compte and not compte.is_superuser and not Personnel.objects.filter(utilisateur=compte).exists() \
                and not hasattr(compte, 'profil_etudiant'):
            compte.delete()
    messages.success(request, f"Le formateur {nom} a été supprimé.")
    return redirect('formateur')


@require_POST
def formateur_acces(request, id):
    """Crée le compte s'il manque, sinon génère un nouveau mot de passe, puis l'envoie."""
    fiche = get_object_or_404(Formateur, id=id)
    mot_de_passe = _mot_de_passe()
    compte = fiche.utilisateur
    if compte is None:
        compte = User.objects.filter(username__iexact=fiche.email).first()
        if compte is None:
            compte = User.objects.create_user(username=fiche.email, email=fiche.email,
                                              first_name=fiche.prenom, last_name=fiche.nom)
        fiche.utilisateur = compte
        fiche.save(update_fields=['utilisateur'])
    compte.set_password(mot_de_passe)
    compte.is_active = True
    compte.save()
    _signaler_acces(request, fiche, mot_de_passe)
    return redirect('formateur')


@require_POST
def formateur_activer(request, id):
    fiche = get_object_or_404(Formateur, id=id)
    if fiche.utilisateur:
        fiche.utilisateur.is_active = not fiche.utilisateur.is_active
        fiche.utilisateur.save(update_fields=['is_active'])
        etat = "réactivé" if fiche.utilisateur.is_active else "désactivé"
        messages.success(request, f"Le compte de {fiche} a été {etat}.")
    return redirect('formateur')
