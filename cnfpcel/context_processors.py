from . import roles


def espace(request):
    """Informations communes aux espaces de gestion et formateur."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {}

    role = roles.role_de(user)
    donnees = {
        'cnf_role': role,
        'cnf_role_libelle': roles.LIBELLES.get(role, ''),
        'cnf_personnel': roles.personnel_de(user),
        'cnf_formateur': roles.formateur_de(user),
    }
    if role == roles.PERSONNEL:
        from .models import Formation, Inscription, MessageContact
        donnees['nb_messages_non_lus'] = MessageContact.objects.filter(lu=False).count()
        donnees['nb_inscriptions_attente'] = Inscription.objects.filter(accepte=False).count()
        donnees['nb_formations_a_valider'] = Formation.objects.filter(publiee=False).count()
    return donnees
