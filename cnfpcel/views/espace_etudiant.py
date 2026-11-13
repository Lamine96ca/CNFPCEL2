"""Espace participant : mes formations et passage des évaluations."""
from ._commun import *  # noqa: F401,F403

__all__ = ['formation_etudiant', 'passer_evaluation', 'info_resultat_evaluation', 'temps_ecoule']


def formation_etudiant(request):
    if not request.user.is_authenticated : 
        return redirect('login')
    user=request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = Etudiant.objects.filter(utilisateur=user).first()
    if utilisateur is not None :
        # Récupère toutes les inscriptions de cet étudiant
        inscriptions = Inscription.objects.filter(etudiant=utilisateur).select_related('formation')

        # Liste de toutes les formations
        formations = [ins.formation for ins in inscriptions]

        context = {
            'formation': formations,
        }

        return render(request, 'accueil/list_section_formation/formation_etudiant.html', context)
    messages.success(request, "Vous n'êtes inscrit à aucune formation")
    return redirect('list_formation',0)


def passer_evaluation(request, evaluation_id):
    if not request.user.is_authenticated:
        return redirect('login')

    utilisateur = get_object_or_404(Etudiant, utilisateur=request.user)
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    questions = Question.objects.filter(evaluation=evaluation).order_by('id')

    if request.method == 'GET':
        request.session['evaluation_start'] = timezone.now().isoformat()

    if request.method == 'POST':
        start_time = timezone.datetime.fromisoformat(
            request.session.get('evaluation_start')
        )

        temps_ecoule_minutes = (
            timezone.now() - start_time
        ).total_seconds() / 60

        temps_ecoule = temps_ecoule_minutes > evaluation.duree

        total_questions = questions.count()
        bonnes_reponses = 0

        for question in questions:
            reponse_id = request.POST.get(f'question_{question.id}')
            if reponse_id:
                try:
                    reponse = Reponse.objects.get(
                        id=reponse_id,
                        question=question
                    )
                    if reponse.correcte:
                        bonnes_reponses += 1
                except Reponse.DoesNotExist:
                    pass

        score = 0
        if total_questions > 0:
            score = round(
                (bonnes_reponses / total_questions) * 100,
                2
            )

        reussi = score >= evaluation.note_minimale

        resultat = ResultatEvaluation.objects.create(
            evaluation=evaluation,
            etudiant=utilisateur,
            score=score,
            bonnes_reponses=bonnes_reponses,
            total_questions=total_questions,
            reussi=reussi,
            temps_ecoule=temps_ecoule
        )

        return redirect(
            'info_resultat_evaluation',
            resultat_id=resultat.id
        )

    return render(request, 'accueil/evaluation/passer_evaluation.html', {
        'evaluation': evaluation,
        'questions': questions,
    })


def info_resultat_evaluation(request, resultat_id):
    resultat = get_object_or_404(ResultatEvaluation, id=resultat_id)
    context = {
        'resultat': resultat,
    }
    return render(request, 'accueil/evaluation/resultat_evaluation.html', context)


def temps_ecoule(request) : 
    return render(request, 'accueil/evaluation/temps_ecoule.html',)
