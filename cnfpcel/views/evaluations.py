"""Gestion des évaluations, questions, réponses et résultats."""
from ._commun import *  # noqa: F401,F403
from django.utils.html import escape

__all__ = ['evaluation', 'evaluation_edit', 'evaluation_delete', 'evaluation_side', 'export_evaluation_excel', 'question_evaluation', 'question_evaluation_edit', 'question_evaluation_delete', 'question_evaluation_side', 'export_question_evaluation_excel', 'reponse_question', 'reponse_question_edit', 'reponse_question_delete', 'reponse_question_side', 'export_reponse_question_excel', 'resultat_evaluation', 'resultat_evaluation_delete', 'resultat_evaluation_side', 'export_resultat_evaluaiton_excel']


#EVALUATION
def evaluation(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    form = EvaluationForm()
    show_modal = False
    titre_modal = "Enregistrement"
    titre_btn = "Enregistrer"

    if request.method == 'POST':
        form = EvaluationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Enregistrement effectué avec succès.")
            return redirect('evaluation')
        else:
            show_modal = True

    context = {
        'active':'6-4', 
        'form': form,
        'show_modal': show_modal,
        'utilisateur': utilisateur,
        'titre_modal': titre_modal,
        'titre_btn': titre_btn
    }
    return render(request, 'gestion/evaluation/evaluation.html', context)


def evaluation_edit(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    evaluation_edit = get_object_or_404(Evaluation, id=id)

    form = EvaluationForm(instance=evaluation_edit)

    show_modal = True
    info = ''

    if request.method == 'POST':
        form = EvaluationForm(request.POST, request.FILES, instance=evaluation_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('evaluation')
        
    context = {
        'active':'6-4',
        'form':form,
        'show_modal':show_modal,
        'info':info,
        'utilisateur':utilisateur
    }
    return render(request, 'gestion/evaluation/evaluation.html', context)


def evaluation_delete(request,id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    evaluation = get_object_or_404(Evaluation,id=id)
    evaluation.delete()
    messages.success(request,"Suppression effectuée")
    return redirect('evaluation')


@csrf_exempt
def evaluation_side(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)

    qs = Evaluation.objects.select_related(
        'formation'
    ).order_by('-id')

    if search_value:
        qs = qs.filter(
            Q(titre__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(formation_nom__icontains=search_value)
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        if n.actif :
            actif = f"<span class='badge bg-success'><i class='bi bi-check-circle-fill me-1'></i> Oui</span>"
        else : 
            actif = f"<span class='badge bg-success'><i class='bi bi-eye-slash-fill me-1'></i> Non</span>"
        

        data.append([
            escape(n.formation.nom),
            escape(n.titre),
            n.duree,
            n.note_minimale,
            actif,
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('question_evaluation', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary' title='Gérer les questions'>
                        <i class='bi bi-file-earmark-plus'></i>
                    </a>
                </div>
            """,

            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('resultat_evaluation', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary' title='Voir les résultats'>
                        <i class='bi bi-file-earmark-plus'></i>
                    </a>
                </div>
            """,
            
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('evaluation_edit', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary' title='Editer'>
                        <i class='bi bi-pencil'></i>
                    </a>

                    <a href='#' class='btn btn-sm m-1 btn-outline-danger' 
                        data-bs-toggle='modal' data-bs-target='#deleteModal{n.id}' title='Supprimer'>
                        <i class='bi bi-trash'></i>
                    </a>
                </div>

                <div class='modal fade' id='deleteModal{n.id}' tabindex='-1'>
                    <div class='modal-dialog modal-dialog-centered'>
                        <div class='modal-content'>
                            <div class='modal-header bg-danger text-white'>
                                <h5 class='modal-title'>Confirmation</h5>
                                <button type='button' class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
                            </div>
                            <div class='modal-body'>
                                Voulez-vous supprimer : <strong> L'évaluation  : {escape(n.titre)}</strong> ?   
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('evaluation_delete', args=[n.id])}">
                                    <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                                    <button class='btn btn-danger'>Oui, supprimer</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """
        ])
    return JsonResponse({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": total,
        "data": data,
    })


def export_evaluation_excel(request):

    qs = Evaluation.objects.all()

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Formation"

    # En-têtes
    headers = [
        "Formation", "Titre" "Description", "Durée", "Note", "Actif"
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.formation.nom,
            n.titre,
            n.description,
            n.duree,
            n.note_minimale,
            n.actif,

        ])

    # Auto-ajustement des colonnes
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Réponse HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename=export_evaluation.xlsx'

    wb.save(response)
    return response


#QUESTION EVALUATION
def question_evaluation(request,evaluation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
    evaluation = get_object_or_404(Evaluation,id=evaluation_id)

    show_modal = False
    info = ''
    titre_modal = "Enregistrement"
    titre_btn = "Enregistrer"

    form = QuestionForm() 
    form_reponse = ReponseForm()

            
    if request.method == 'POST' :
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.evaluation = evaluation
            question.save()
            messages.success(request, "Enregistrement effectué avec succès.")
            return redirect('question_evaluation', evaluation_id)       
        else:
            show_modal = True
        
    context = {
        'active':'6-4',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'evaluation':evaluation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
    }
    return render(request, 'gestion/question/question.html', context)


def question_evaluation_edit(request,id,evaluation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    evaluation = get_object_or_404(Evaluation,id=evaluation_id)

    question_edit = get_object_or_404(Question, id=id)


    form = QuestionForm(instance=question_edit)

    show_modal = True
    info = ''
    titre_modal = "Mise à jour"
    titre_btn = "Mise à jour"

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('question_evaluation', evaluation_id)
        
    context = {
        'active':'6-4',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'evaluation':evaluation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
        }
    return render(request, 'gestion/question/question.html', context)


def question_evaluation_delete(request,id,evaluation_id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    evaluation = get_object_or_404(Evaluation,id=evaluation_id)
    question = get_object_or_404(Question,id=id)
    question.delete()
    return redirect('question_evaluation', evaluation_id)


@csrf_exempt
def question_evaluation_side(request, evaluation_id):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    qs = Question.objects.filter(evaluation=evaluation).order_by('id')
    qs = qs.select_related('evaluation')

    if search_value:
        qs = qs.filter(
            Q(texte__icontains=search_value) |
            Q(evaluation__titre__icontains=search_value)
        )

    total = qs.count()
    filtered = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:

        data.append([
            escape(n.texte),
            escape(n.evaluation.titre),

            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('reponse_question', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary'>
                        <i class='bi bi-file-earmark-plus'></i>
                    </a>
                </div>
            """,

            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('question_evaluation_edit', args=[n.id, n.evaluation_id])}' 
                        class='btn btn-sm m-1 btn-outline-primary'>
                        <i class='bi bi-pencil'></i>
                    </a>

                    <a href='#' class='btn btn-sm m-1 btn-outline-danger' 
                       data-bs-toggle='modal' data-bs-target='#deleteModal{n.id}'>
                        <i class='bi bi-trash'></i>
                    </a>
                </div>

                <div class='modal fade' id='deleteModal{n.id}' tabindex='-1'>
                    <div class='modal-dialog modal-dialog-centered'>
                        <div class='modal-content'>
                            <div class='modal-header bg-danger text-white'>
                                <h5 class='modal-title'>Confirmation</h5>
                                <button type='button' class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
                            </div>
                            <div class='modal-body'>
                                Voulez-vous supprimer la question : <strong>{escape(n.texte)}</strong> ?
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('question_evaluation_delete', args=[n.id, n.evaluation_id])}">
                                    <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                                    <button class='btn btn-danger'>Oui, supprimer</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """
        ])

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered,
        "data": data,
    })


def export_question_evaluation_excel(request):

    qs = Question.objects.select_related('evaluation')

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "question"

    # En-têtes
    headers = [
        "Texte", "Evaluation",
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.texte,
            n.evaluation.titre,
        ])

    # Auto-ajustement des colonnes
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Réponse HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename=export_question_evaluation.xlsx'

    wb.save(response)
    return response


#REPONSES AUX QUESTIONS
def reponse_question(request, question_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    question = get_object_or_404(Question,id=question_id)
    evaluation = get_object_or_404(Evaluation,id=question.evaluation_id)
    formation = get_object_or_404(Formation, id=evaluation.formation_id)

    show_modal = False
    info = ''
    titre_modal = "Enregistrement"
    titre_btn = "Enregistrer"

    form = ReponseForm() 
            
    if request.method == 'POST' :
        form = ReponseForm(request.POST, request.FILES)
        if form.is_valid():
            reponse = form.save(commit=False)
            reponse.question = question
            reponse.save()
            messages.success(request, "Enregistrement effectué avec succès.")
            return redirect('reponse_question', question.id)       
        else:
            show_modal = True
        
    context = {
        'active':'6-4',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'question':question,
        'formation':formation,
        'evaluation':evaluation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
    }
    return render(request, 'gestion/reponse/reponse.html', context)


def reponse_question_edit(request,id, question_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    question = get_object_or_404(Question,id=question_id)
    evaluation = get_object_or_404(Evaluation,id=question.evaluation_id)
    formation = get_object_or_404(Formation, id=evaluation.formation_id)

    reponse_edit = get_object_or_404(Reponse, id=id)


    form = ReponseForm(instance=reponse_edit)

    show_modal = True
    info = ''
    titre_modal = "Mise à jour"
    titre_btn = "Mise à jour"

    if request.method == 'POST':
        form = ReponseForm(request.POST, request.FILES, instance=reponse_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('reponse_question', question.id)
        
    context = {
        'active':'6-4',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'question':question,
        'formation':formation,
        'evaluation':evaluation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
    }
    return render(request, 'gestion/reponse/reponse.html', context)


def reponse_question_delete(request,id, question_id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    question = get_object_or_404(Question,id=question_id)
    reponse = get_object_or_404(reponse,id=id)
    reponse.delete()
    return redirect('reponse_question', question.id)


@csrf_exempt
def reponse_question_side(request, question_id):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    question = get_object_or_404(Question, id=question_id)
    qs = Reponse.objects.filter(question=question).select_related('question')

    if search_value:
        qs = qs.filter(
            Q(texte__icontains=search_value) |
            Q(question__texte__icontains=search_value)
        )

    total = qs.count()
    filtered = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:

        if n.correcte :
            correcte = f"<span class='badge bg-success'><i class='bi bi-check-circle-fill me-1'></i> Oui</span>"
        else:
            correcte = f"<span class='badge bg-danger'><i class='bi bi-x-circle-fill me-1'></i> Non</span>"


        data.append([
            escape(n.texte),
            escape(n.question.texte),
            correcte,

            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('reponse_question_edit', args=[n.id, question.id])}' 
                        class='btn btn-sm m-1 btn-outline-primary'>
                        <i class='bi bi-pencil'></i>
                    </a>

                    <a href='#' class='btn btn-sm m-1 btn-outline-danger' 
                       data-bs-toggle='modal' data-bs-target='#deleteModal{n.id}'>
                        <i class='bi bi-trash'></i>
                    </a>
                </div>

                <div class='modal fade' id='deleteModal{n.id}' tabindex='-1'>
                    <div class='modal-dialog modal-dialog-centered'>
                        <div class='modal-content'>
                            <div class='modal-header bg-danger text-white'>
                                <h5 class='modal-title'>Confirmation</h5>
                                <button type='button' class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
                            </div>
                            <div class='modal-body'>
                                Voulez-vous supprimer la reponse: <strong>{escape(n.texte)}</strong> ?
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('reponse_question_delete', args=[n.id, question.id])}">
                                    <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                                    <button class='btn btn-danger'>Oui, supprimer</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """
        ])

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered,
        "data": data,
    })


def export_reponse_question_excel(request):

    qs = Reponse.objects.select_related('question')

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "question"

    # En-têtes
    headers = [
        "Reponse", "Question", "Correcte"
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.texte,
            n.question.texte,
            n.correcte,
        ])

    # Auto-ajustement des colonnes
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Réponse HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename=export_question_evaluation.xlsx'

    wb.save(response)
    return response


def resultat_evaluation(request, evaluation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    evaluation = get_object_or_404(Evaluation,id=evaluation_id)
   
    context = {
        'active' :'resultat_evaluation',
        'utilisateur':utilisateur,
        'evaluation':evaluation,
    }

    return render(request, 'gestion/resultat/resultat.html', context)


def resultat_evaluation_delete(request,id,evaluation_id) : 
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    evaluation = get_object_or_404(Evaluation,id=evaluation_id)
    resultat = get_object_or_404(ResultatEvaluation, id=id)
    resultat.delete()
    messages.success(request,'suppréssion effectuée avec succès')
    return redirect('resultat_evaluation', evaluation.id)


@csrf_exempt
def resultat_evaluation_side(request, evaluation_id):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    qs = ResultatEvaluation.objects.filter(
        evaluation=evaluation
    ).select_related('evaluation', 'etudiant')

    total = qs.count()

    if search_value:
        qs = qs.filter(
            Q(etudiant__prenom__icontains=search_value) |
            Q(etudiant__nom__icontains=search_value) |
            Q(evaluation__titre__icontains=search_value)
        )

    filtered = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        score = (
            f"<span class='badge bg-success'>{n.score}</span>"
            if n.score >= evaluation.note_minimale
            else f"<span class='badge bg-danger'>{n.score}</span>"
        )

        etudiant = escape(f"{n.etudiant.prenom} {n.etudiant.nom}")

        data.append([
            etudiant,
            escape(n.etudiant.telephone),
            escape(n.etudiant.email),
            escape(n.evaluation.formation.nom),
            score,
            n.date_passage.strftime("%d/%m/%Y"),
            f"""
            <div class="d-flex justify-content-center">
                <a href='#' class='btn btn-sm btn-outline-danger'
                   data-bs-toggle='modal'
                   data-bs-target='#deleteModal{n.id}'>
                    <i class='bi bi-trash'></i>
                </a>
            </div>

            <div class='modal fade' id='deleteModal{n.id}' tabindex='-1'>
                <div class='modal-dialog modal-dialog-centered'>
                    <div class='modal-content'>
                        <div class='modal-header bg-danger text-white'>
                            <h5 class='modal-title'>Confirmation</h5>
                            <button type='button' class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
                        </div>
                        <div class='modal-body'>
                            Voulez-vous supprimer le résultat de <strong>{etudiant}</strong> ?
                        </div>
                        <div class='modal-footer'>
                            <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                            <form method='post'
                                  action="{reverse('resultat_evaluation_delete', args=[n.id, n.evaluation_id])}">
                                <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                                <button class='btn btn-danger'>Oui, supprimer</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            """
        ])

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total,
        "recordsFiltered": filtered,
        "data": data,
    })


def export_resultat_evaluaiton_excel(request):

    qs = ResultatEvaluation.objects.select_related('evaluation','etudiant')

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Reponse"

    # En-têtes
    headers = [
        "Prénom", "Nom", "Téléphone", "E-mail", "Evaluaiton", "Scre", "Date"
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        date_passage = n.date_passage.strftime("%d/%m/%Y %H:%M")
        ws.append([
            n.etudiant.prenom,
            n.etudiant.nom,
            n.etudiant.telephone,
            n.etudiant.email,
            n.evaluation.titre,
            n.score,
            date_passage
        ])

    # Auto-ajustement des colonnes
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Réponse HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename=export_question_evaluation.xlsx'

    wb.save(response)
    return response
