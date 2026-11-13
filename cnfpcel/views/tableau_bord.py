"""Tableau de bord de la gestion."""
from ._commun import *  # noqa: F401,F403

__all__ = ['gestion']


def gestion(request):
    """Tableau de bord de la gestion (accès réservé au personnel par roles.AccesMiddleware)."""
    from django.db.models import Count
    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    now = timezone.now()

    total_formation = Formation.objects.count()
    total_formation_active = Formation.objects.filter(active=True).count()
    total_inscription = Inscription.objects.count()
    total_inscription_attente = Inscription.objects.filter(accepte=False).count()
    total_article = TitreArticle.objects.count()
    total_article_pub = TitreArticle.objects.filter(statut=True).count()
    total_message = MessageContact.objects.count()
    total_message_non_lu = MessageContact.objects.filter(lu=False).count()
    total_resultat = ResultatEvaluation.objects.count()
    total_reussi = ResultatEvaluation.objects.filter(reussi=True).count()

    def pct(a, b):
        return round(a * 100 / b) if b else 0

    formations_stats = (Formation.objects
                        .annotate(nb_inscrits=Count('inscription', distinct=True),
                                  nb_formateurs=Count('formation_dispenser', distinct=True))
                        .order_by('-nb_inscrits', 'nom')[:8])

    context = {
        'active': 1,
        'utilisateur': utilisateur,
        'personnel': utilisateur,
        'maintenant': now,

        'total_personnel': Personnel.objects.count(),
        'total_etudiant': Etudiant.objects.count(),
        'total_inscription': total_inscription,
        'total_inscription_attente': total_inscription_attente,
        'pct_inscription_acceptee': pct(total_inscription - total_inscription_attente, total_inscription),
        'total_formation': total_formation,
        'pct_formation_active': pct(total_formation_active, total_formation),
        'total_domaine': DomaineFormation.objects.count(),
        'total_formateur': Formateur.objects.count(),
        'total_evaluation': Evaluation.objects.count(),
        'total_resultat': total_resultat,
        'pct_reussite': pct(total_reussi, total_resultat),
        'total_article': total_article,
        'total_article_pub': total_article_pub,
        'pct_article_pub': pct(total_article_pub, total_article),
        'total_message': total_message,
        'total_message_non_lu': total_message_non_lu,
        'total_evenement': Evenement.objects.filter(date__gte=now.date()).count(),

        'inscriptions_attente': (Inscription.objects.filter(accepte=False)
                                 .select_related('etudiant', 'formation')
                                 .order_by('-date_inscription')[:6]),
        'formations_a_valider': (Formation.objects.filter(publiee=False)
                                 .select_related('cree_par', 'domaine').order_by('-id')),
        'derniers_messages': MessageContact.objects.order_by('-date_envoi')[:5],
        'prochains_evenements': Evenement.objects.filter(date__gte=now.date()).order_by('date')[:4],
        'formations_stats': formations_stats,
        'graphe_formations': [f.nom[:40] for f in formations_stats],
        'graphe_inscrits': [f.nb_inscrits for f in formations_stats],
    }
    return render(request, 'gestion/tableau_bord.html', context)
