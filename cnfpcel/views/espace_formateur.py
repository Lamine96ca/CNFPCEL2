"""
Espace formateur.

Un formateur ne voit et ne modifie que les formations qui lui sont attribuées
(table `DispenseFormation`). Toutes les vues passent par `roles.formateur_requis`.
"""
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import (EvaluationFormateurForm, FormateurProfilForm, FormationFormateurForm, QuestionForm,
                    ReponseForm, RessourceFormationForm, SectionFormationForm)
from ..models import (DispenseFormation, Evaluation, Formation, Inscription, Question, Reponse,
                     RessourceFormation, ResultatEvaluation, SectionFormation)
from ..roles import formateur_requis

ONGLETS = ('sections', 'ressources', 'evaluations', 'participants', 'resultats')


# ------------------------------------------------------------------ outils
def _mes_formations(formateur):
    return Formation.objects.filter(formation_dispenser__formateur=formateur).distinct()


def _ma_formation(formateur, formation_id):
    return get_object_or_404(_mes_formations(formateur), id=formation_id)


def _mon_evaluation(formateur, evaluation_id):
    return get_object_or_404(Evaluation.objects.select_related('formation'),
                             id=evaluation_id, formation__in=_mes_formations(formateur))


def _vers_formation(formation, onglet):
    return redirect(f"/espace-formateur/formation/{formation.id}/?onglet={onglet}")


def _erreurs(request, form):
    for champ, erreurs in form.errors.items():
        for e in erreurs:
            messages.error(request, e if champ == '__all__' else f"{form.fields[champ].label if champ in form.fields else champ} : {e}")


def _page_formulaire(request, formateur, *, titre, form, retour, formation, multipart=False, icone='bi-pencil-square'):
    return render(request, 'formateur/formulaire.html', {
        'formateur': formateur, 'titre': titre, 'form': form, 'retour': retour,
        'formation': formation, 'multipart': multipart, 'icone': icone, 'actif': 'formations',
    })


# ------------------------------------------------------------------ accueil
@formateur_requis
def espace_formateur(request, formateur):
    formations = (_mes_formations(formateur)
                  .annotate(nb_sections=Count('sections', distinct=True),
                            nb_ressources=Count('ressourceformation', distinct=True),
                            nb_evaluations=Count('evaluation', distinct=True),
                            nb_inscrits=Count('inscription', filter=Q(inscription__accepte=True), distinct=True))
                  .select_related('domaine').order_by('nom'))

    resultats = (ResultatEvaluation.objects
                 .filter(evaluation__formation__in=_mes_formations(formateur))
                 .select_related('etudiant', 'evaluation', 'evaluation__formation'))
    stats = resultats.aggregate(moyenne=Avg('score'), total=Count('id'),
                                reussis=Count('id', filter=Q(reussi=True)))

    return render(request, 'formateur/accueil.html', {
        'formateur': formateur,
        'actif': 'accueil',
        'formations': formations,
        'total_inscrits': sum(f.nb_inscrits for f in formations),
        'total_evaluations': sum(f.nb_evaluations for f in formations),
        'stats': stats,
        'taux_reussite': round(stats['reussis'] * 100 / stats['total']) if stats['total'] else 0,
        'derniers_resultats': resultats.order_by('-date_passage')[:6],
    })


@formateur_requis
def espace_formateur_formations(request, formateur):
    formations = (_mes_formations(formateur)
                  .annotate(nb_sections=Count('sections', distinct=True),
                            nb_ressources=Count('ressourceformation', distinct=True),
                            nb_evaluations=Count('evaluation', distinct=True),
                            nb_inscrits=Count('inscription', filter=Q(inscription__accepte=True), distinct=True))
                  .select_related('domaine').order_by('nom'))
    return render(request, 'formateur/formations.html', {
        'formateur': formateur, 'actif': 'formations', 'formations': formations,
    })


# ------------------------------------------------------------------ proposer / modifier une formation
@formateur_requis
def espace_formateur_formation_ajout(request, formateur):
    form = FormationFormateurForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            formation = form.save(commit=False)
            formation.publiee = False          # en attente de validation par l'administration
            formation.cree_par = formateur
            formation.save()
            DispenseFormation.objects.create(formateur=formateur, formation=formation)
        messages.success(request, "Formation créée. Préparez son contenu : elle sera visible sur le site "
                                  "dès que l'administration l'aura validée.")
        return redirect('espace_formateur_formation', formation.id)
    return _page_formulaire(request, formateur, titre="Proposer une formation", form=form, multipart=True,
                            retour='/espace-formateur/formations/', formation=None, icone='bi-mortarboard')


@formateur_requis
def espace_formateur_formation_modif(request, formateur, formation_id):
    formation = _ma_formation(formateur, formation_id)
    form = FormationFormateurForm(request.POST or None, request.FILES or None, instance=formation)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Les informations de la formation ont été mises à jour.")
        return redirect('espace_formateur_formation', formation.id)
    return _page_formulaire(request, formateur, titre="Modifier la formation", form=form, multipart=True,
                            retour=f"/espace-formateur/formation/{formation.id}/", formation=formation,
                            icone='bi-mortarboard')


@formateur_requis
@require_POST
def espace_formateur_formation_suppr(request, formateur, formation_id):
    """Un formateur ne peut retirer qu'une formation qu'il a proposée et qui n'est pas encore publiée."""
    formation = _ma_formation(formateur, formation_id)
    if formation.publiee or formation.cree_par_id != formateur.id:
        messages.error(request, "Seule une formation que vous avez proposée et non encore publiée peut être retirée.")
        return redirect('espace_formateur_formation', formation.id)
    nom = formation.nom
    formation.delete()
    messages.success(request, f"La proposition « {nom} » a été retirée.")
    return redirect('espace_formateur_formations')


# ------------------------------------------------------------------ formation
@formateur_requis
def espace_formateur_formation(request, formateur, formation_id):
    formation = _ma_formation(formateur, formation_id)
    onglet = request.GET.get('onglet', 'sections')
    if onglet not in ONGLETS:
        onglet = 'sections'

    evaluations = (Evaluation.objects.filter(formation=formation)
                   .annotate(nb_questions=Count('question', distinct=True),
                             nb_resultats=Count('resultatevaluation', distinct=True))
                   .order_by('titre'))
    inscriptions = (Inscription.objects.filter(formation=formation, accepte=True)
                    .select_related('etudiant').order_by('etudiant__nom', 'etudiant__prenom'))
    resultats = (ResultatEvaluation.objects.filter(evaluation__formation=formation)
                 .select_related('etudiant', 'evaluation').order_by('-date_passage'))

    return render(request, 'formateur/formation.html', {
        'formateur': formateur,
        'actif': 'formations',
        'formation': formation,
        'onglet': onglet,
        'sections': formation.sections.order_by('id'),
        'ressources': RessourceFormation.objects.filter(formation=formation).order_by('titre'),
        'evaluations': evaluations,
        'inscriptions': inscriptions,
        'nb_attente': Inscription.objects.filter(formation=formation, accepte=False).count(),
        'resultats': resultats,
        'moyenne': resultats.aggregate(m=Avg('score'))['m'],
        'form_section': SectionFormationForm(),
        'form_ressource': RessourceFormationForm(),
        'form_evaluation': EvaluationFormateurForm(formation=formation),
    })


# ------------------------------------------------------------------ sections
@formateur_requis
@require_POST
def espace_formateur_section_ajout(request, formateur, formation_id):
    formation = _ma_formation(formateur, formation_id)
    form = SectionFormationForm(request.POST, instance=SectionFormation(formation=formation))
    if form.is_valid():
        form.save()
        messages.success(request, "Section ajoutée.")
    else:
        _erreurs(request, form)
    return _vers_formation(formation, 'sections')


@formateur_requis
def espace_formateur_section_modif(request, formateur, id):
    section = get_object_or_404(SectionFormation, id=id, formation__in=_mes_formations(formateur))
    form = SectionFormationForm(request.POST or None, instance=section)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Section modifiée.")
        return _vers_formation(section.formation, 'sections')
    return _page_formulaire(request, formateur, titre="Modifier la section", form=form,
                            retour=f"/espace-formateur/formation/{section.formation_id}/?onglet=sections",
                            formation=section.formation, icone='bi-list-columns')


@formateur_requis
@require_POST
def espace_formateur_section_suppr(request, formateur, id):
    section = get_object_or_404(SectionFormation, id=id, formation__in=_mes_formations(formateur))
    formation = section.formation
    section.delete()
    messages.success(request, "Section supprimée.")
    return _vers_formation(formation, 'sections')


# ------------------------------------------------------------------ ressources
def _ressource_en_double(formation, titre, exclure=None):
    qs = RessourceFormation.objects.filter(formation=formation, titre__iexact=titre)
    if exclure:
        qs = qs.exclude(pk=exclure)
    return qs.exists()


@formateur_requis
@require_POST
def espace_formateur_ressource_ajout(request, formateur, formation_id):
    formation = _ma_formation(formateur, formation_id)
    form = RessourceFormationForm(request.POST, request.FILES, instance=RessourceFormation(formation=formation))
    if form.is_valid():
        if _ressource_en_double(formation, form.cleaned_data['titre']):
            messages.error(request, "Une ressource porte déjà ce titre dans cette formation.")
        elif not form.cleaned_data.get('pdf') and not form.cleaned_data.get('video'):
            messages.error(request, "Ajoutez au moins un fichier PDF ou une vidéo.")
        else:
            form.save()
            messages.success(request, "Ressource ajoutée.")
    else:
        _erreurs(request, form)
    return _vers_formation(formation, 'ressources')


@formateur_requis
def espace_formateur_ressource_modif(request, formateur, id):
    ressource = get_object_or_404(RessourceFormation, id=id, formation__in=_mes_formations(formateur))
    form = RessourceFormationForm(request.POST or None, request.FILES or None, instance=ressource)
    if request.method == 'POST' and form.is_valid():
        if _ressource_en_double(ressource.formation, form.cleaned_data['titre'], exclure=ressource.pk):
            form.add_error('titre', "Une ressource porte déjà ce titre dans cette formation.")
        else:
            form.save()
            messages.success(request, "Ressource modifiée.")
            return _vers_formation(ressource.formation, 'ressources')
    return _page_formulaire(request, formateur, titre="Modifier la ressource", form=form, multipart=True,
                            retour=f"/espace-formateur/formation/{ressource.formation_id}/?onglet=ressources",
                            formation=ressource.formation, icone='bi-folder2-open')


@formateur_requis
@require_POST
def espace_formateur_ressource_suppr(request, formateur, id):
    ressource = get_object_or_404(RessourceFormation, id=id, formation__in=_mes_formations(formateur))
    formation = ressource.formation
    ressource.delete()
    messages.success(request, "Ressource supprimée.")
    return _vers_formation(formation, 'ressources')


# ------------------------------------------------------------------ évaluations
@formateur_requis
@require_POST
def espace_formateur_evaluation_ajout(request, formateur, formation_id):
    formation = _ma_formation(formateur, formation_id)
    form = EvaluationFormateurForm(request.POST, formation=formation, instance=Evaluation(formation=formation))
    if form.is_valid():
        evaluation = form.save()
        messages.success(request, "Évaluation créée. Ajoutez maintenant ses questions.")
        return redirect('espace_formateur_evaluation', evaluation.id)
    _erreurs(request, form)
    return _vers_formation(formation, 'evaluations')


@formateur_requis
def espace_formateur_evaluation_modif(request, formateur, id):
    evaluation = _mon_evaluation(formateur, id)
    form = EvaluationFormateurForm(request.POST or None, instance=evaluation, formation=evaluation.formation)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Évaluation modifiée.")
        return redirect('espace_formateur_evaluation', evaluation.id)
    return _page_formulaire(request, formateur, titre="Modifier l'évaluation", form=form,
                            retour=f"/espace-formateur/evaluation/{evaluation.id}/",
                            formation=evaluation.formation, icone='bi-ui-checks')


@formateur_requis
@require_POST
def espace_formateur_evaluation_suppr(request, formateur, id):
    evaluation = _mon_evaluation(formateur, id)
    formation = evaluation.formation
    evaluation.delete()
    messages.success(request, "Évaluation supprimée.")
    return _vers_formation(formation, 'evaluations')


@formateur_requis
def espace_formateur_evaluation(request, formateur, id):
    evaluation = _mon_evaluation(formateur, id)
    questions = Question.objects.filter(evaluation=evaluation).prefetch_related('reponse_set').order_by('id')
    resultats = (ResultatEvaluation.objects.filter(evaluation=evaluation)
                 .select_related('etudiant').order_by('-date_passage'))
    sans_bonne_reponse = [q for q in questions if not any(r.correcte for r in q.reponse_set.all())]
    return render(request, 'formateur/evaluation.html', {
        'formateur': formateur,
        'actif': 'formations',
        'evaluation': evaluation,
        'formation': evaluation.formation,
        'questions': questions,
        'sans_bonne_reponse': sans_bonne_reponse,
        'resultats': resultats,
        'stats': resultats.aggregate(moyenne=Avg('score'), total=Count('id'),
                                     reussis=Count('id', filter=Q(reussi=True))),
        'form_question': QuestionForm(),
        'form_reponse': ReponseForm(),
    })


# ------------------------------------------------------------------ questions
@formateur_requis
@require_POST
def espace_formateur_question_ajout(request, formateur, evaluation_id):
    evaluation = _mon_evaluation(formateur, evaluation_id)
    form = QuestionForm(request.POST, instance=Question(evaluation=evaluation))
    if form.is_valid():
        texte = form.cleaned_data['texte']
        if Question.objects.filter(evaluation=evaluation, texte__iexact=texte).exists():
            messages.error(request, "Cette question existe déjà dans l'évaluation.")
        else:
            question = form.save()
            # Réponses saisies directement avec la question (facultatif)
            textes = request.POST.getlist('reponse_texte')
            correcte = request.POST.get('reponse_correcte')
            for i, t in enumerate(textes):
                if t.strip():
                    Reponse.objects.create(question=question, texte=t.strip(), correcte=(str(i) == correcte))
            messages.success(request, "Question ajoutée.")
    else:
        _erreurs(request, form)
    return redirect('espace_formateur_evaluation', evaluation.id)


@formateur_requis
def espace_formateur_question_modif(request, formateur, id):
    question = get_object_or_404(Question.objects.select_related('evaluation__formation'),
                                 id=id, evaluation__formation__in=_mes_formations(formateur))
    form = QuestionForm(request.POST or None, instance=question)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Question modifiée.")
        return redirect('espace_formateur_evaluation', question.evaluation_id)
    return _page_formulaire(request, formateur, titre="Modifier la question", form=form,
                            retour=f"/espace-formateur/evaluation/{question.evaluation_id}/",
                            formation=question.evaluation.formation, icone='bi-question-circle')


@formateur_requis
@require_POST
def espace_formateur_question_suppr(request, formateur, id):
    question = get_object_or_404(Question, id=id, evaluation__formation__in=_mes_formations(formateur))
    evaluation_id = question.evaluation_id
    question.delete()
    messages.success(request, "Question supprimée.")
    return redirect('espace_formateur_evaluation', evaluation_id)


# ------------------------------------------------------------------ réponses
@formateur_requis
@require_POST
def espace_formateur_reponse_ajout(request, formateur, question_id):
    question = get_object_or_404(Question, id=question_id, evaluation__formation__in=_mes_formations(formateur))
    form = ReponseForm(request.POST, instance=Reponse(question=question))
    if form.is_valid():
        if Reponse.objects.filter(question=question, texte__iexact=form.cleaned_data['texte']).exists():
            messages.error(request, "Cette réponse existe déjà pour la question.")
        else:
            form.save()
            messages.success(request, "Réponse ajoutée.")
    else:
        _erreurs(request, form)
    return redirect(f"/espace-formateur/evaluation/{question.evaluation_id}/#question-{question.id}")


@formateur_requis
def espace_formateur_reponse_modif(request, formateur, id):
    reponse = get_object_or_404(Reponse.objects.select_related('question__evaluation__formation'),
                                id=id, question__evaluation__formation__in=_mes_formations(formateur))
    form = ReponseForm(request.POST or None, instance=reponse)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Réponse modifiée.")
        return redirect(f"/espace-formateur/evaluation/{reponse.question.evaluation_id}/#question-{reponse.question_id}")
    return _page_formulaire(request, formateur, titre="Modifier la réponse", form=form,
                            retour=f"/espace-formateur/evaluation/{reponse.question.evaluation_id}/",
                            formation=reponse.question.evaluation.formation, icone='bi-check2-square')


@formateur_requis
@require_POST
def espace_formateur_reponse_suppr(request, formateur, id):
    reponse = get_object_or_404(Reponse, id=id, question__evaluation__formation__in=_mes_formations(formateur))
    question = reponse.question
    reponse.delete()
    messages.success(request, "Réponse supprimée.")
    return redirect(f"/espace-formateur/evaluation/{question.evaluation_id}/#question-{question.id}")


# ------------------------------------------------------------------ profil
@formateur_requis
def espace_formateur_profil(request, formateur):
    form = FormateurProfilForm(instance=formateur)
    form_mdp = PasswordChangeForm(request.user)
    for champ in form_mdp.fields.values():
        champ.widget.attrs['class'] = 'form-control'

    if request.method == 'POST':
        if 'changer_mdp' in request.POST:
            form_mdp = PasswordChangeForm(request.user, request.POST)
            for champ in form_mdp.fields.values():
                champ.widget.attrs['class'] = 'form-control'
            if form_mdp.is_valid():
                user = form_mdp.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Votre mot de passe a été modifié.")
                return redirect('espace_formateur_profil')
        else:
            form = FormateurProfilForm(request.POST, instance=formateur)
            if form.is_valid():
                form.save()
                messages.success(request, "Votre profil a été mis à jour.")
                return redirect('espace_formateur_profil')

    return render(request, 'formateur/profil.html', {
        'formateur': formateur, 'actif': 'profil', 'form': form, 'form_mdp': form_mdp,
        'formations': _mes_formations(formateur).order_by('nom'),
    })
