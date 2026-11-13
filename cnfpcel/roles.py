"""
Rôles CNFPATEL et contrôle d'accès centralisé.

- Personnel  : compte lié à un `Personnel` (ou super-utilisateur). Accède à la gestion.
- Formateur  : compte lié à un `Formateur`. Accède à l'espace formateur, limité à ses formations.
- Étudiant   : compte lié à un `Etudiant`. Accède à « Mes formations ».

Le middleware `AccesMiddleware` protège toutes les pages de gestion sans avoir à
répéter la vérification dans chaque vue : toute page de l'application qui n'est
ni publique, ni de l'espace formateur, ni de l'espace étudiant exige un personnel.
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

PERSONNEL = 'personnel'
FORMATEUR = 'formateur'
ETUDIANT = 'etudiant'

LIBELLES = {
    PERSONNEL: 'Administration',
    FORMATEUR: 'Formateur',
    ETUDIANT: 'Participant',
}

# Pages accessibles à tous (site public, connexion, passage des évaluations…)
PAGES_PUBLIQUES = {
    'index', 'page_indisponible', 'personnel_liste',
    'login', 'logout', 'mot_de_passe_oublie',
    'detail_article', 'article_liste',
    'evenement_detail', 'evenement_liste',
    'list_formation', 'list_section_formation', 'galerie_index',
    'recherche_index',
    # Espace étudiant (chaque vue vérifie déjà le profil étudiant)
    'formation_etudiant', 'passer_evaluation', 'info_resultat_evaluation', 'temps_ecoule',
}

PREFIXE_FORMATEUR = 'espace_formateur'


def _profil(user, nom):
    try:
        return getattr(user, nom)
    except Exception:
        return None


def personnel_de(user):
    return _profil(user, 'profil_personnel') if user.is_authenticated else None


def formateur_de(user):
    return _profil(user, 'profil_formateur') if user.is_authenticated else None


def etudiant_de(user):
    return _profil(user, 'profil_etudiant') if user.is_authenticated else None


def role_de(user):
    if not user.is_authenticated:
        return None
    if personnel_de(user) or user.is_superuser:
        return PERSONNEL
    if formateur_de(user):
        return FORMATEUR
    if etudiant_de(user):
        return ETUDIANT
    return None


def page_accueil(user):
    """Nom d'URL de la page d'accueil de l'utilisateur selon son rôle."""
    return {
        PERSONNEL: 'gestion',
        FORMATEUR: 'espace_formateur',
        ETUDIANT: 'formation_etudiant',
    }.get(role_de(user), 'index')


def est_personnel(user):
    return role_de(user) == PERSONNEL


def formateur_requis(vue):
    """Décorateur : réserve la vue aux formateurs et leur passe `formateur`."""
    @wraps(vue)
    def enveloppe(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_active:
            return redirect('login')
        formateur = formateur_de(request.user)
        if formateur is None:
            messages.error(request, "Cet espace est réservé aux formateurs.")
            return redirect(page_accueil(request.user))
        return vue(request, formateur, *args, **kwargs)
    return enveloppe


class AccesMiddleware:
    """Bloque l'accès aux pages de gestion pour tout compte qui n'est pas du personnel."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return None
        # Seules les vues de l'application cnfpcel sont concernées (admin, médias… exclus)
        if not match.func.__module__.startswith('cnfpcel.'):
            return None
        nom = match.url_name or ''
        if nom in PAGES_PUBLIQUES or nom.startswith(PREFIXE_FORMATEUR):
            return None

        user = request.user
        if not user.is_authenticated or not user.is_active:
            return redirect('login')
        if est_personnel(user):
            return None
        messages.error(request, "Vous n'avez pas accès à l'espace de gestion.")
        return redirect(page_accueil(user))
