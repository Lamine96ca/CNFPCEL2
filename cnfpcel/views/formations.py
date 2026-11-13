"""Gestion des domaines, formations, sections et ressources."""
from ._commun import *  # noqa: F401,F403
from django.utils.html import escape
from django.views.decorators.http import require_POST

__all__ = ['domaine_formation', 'domaine_formation_edit', 'domaine_formation_delete', 'domaine_formation_side', 'export_domaine_formation_excel', 'formation', 'formation_edit', 'formation_delete', 'formation_side', 'formation_publier', 'export_formation_excel', 'sectionformation', 'sectionformation_edit', 'sectionformation_delete', 'sectionformation_side', 'export_sectionformation_excel', 'ressourceformation', 'ressourceformation_edit', 'ressourceformation_delete', 'ressource_formation_side', 'export_ressourceformation_excel']


def domaine_formation(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
            
            domaine_formation_list = DomaineFormation.objects.all().order_by('-id')  # Tri par ID décroissant

            show_modal = False
            info = ''
            titre_modal = "Enregistrement"
            titre_btn = "Enregistrer"
            
            if request.method == 'POST' :
                form = DomaineFormationForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Enregistrement effectué avec succès.")
                    return redirect('domaine_formation')
                
                else:
                    show_modal = True
                    context = {
                        'active':6,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'domaine_formation':domaine_formation,
                        'utilisateur':utilisateur
                    }
                    return render(request, 'gestion/domaine_formation/domaine_formation.html', context)
                
            else:
                form = DomaineFormationForm() 
                context = {
                    'active':6,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'domaine_formation':domaine_formation_list,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
            return render(request, 'gestion/domaine_formation/domaine_formation.html', context)
        
    return redirect('login')


def domaine_formation_edit(request,id) :
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    domaine_formation_edit = get_object_or_404(DomaineFormation, id=id)

    domaine_formation_list = DomaineFormation.objects.all().order_by('-id')  # Tri par ID décroissant
    
    form = DomaineFormationForm(instance=domaine_formation_edit)

    show_modal = True
    info = ''
    titre_modal = "Mise à jour"
    titre_btn = "Mettre à jour"

    if request.method == 'POST':
        form = DomaineFormationForm(request.POST, request.FILES, instance=domaine_formation_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('domaine_formation')
        
    context = {
        'active':6,
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'domaine_formation':domaine_formation_list,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn
        }
    return render(request, 'gestion/domaine_formation/domaine_formation.html', context)


def domaine_formation_delete(request,id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    domaine_formation = get_object_or_404(DomaineFormation,id=id)
    domaine_formation.delete()
    return redirect('domaine_formation')


@csrf_exempt
def domaine_formation_side(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)

    qs = DomaineFormation.objects.all()

    if search_value:
        qs = qs.filter(
            Q(nom__icontains=search_value) |
            Q(description__icontains=search_value)
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        # Sécurisation image
        try:
            img_url = n.image.url
        except:
            img_url = '/static/default.png'

        data.append([
            f"<img src='{img_url}' alt='image' style='width:60px; height:60px; object-fit:cover; border-radius:5px;'>",
            n.nom,
            (n.description[:80] + '...') if len(n.description) > 80 else n.description,
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('domaine_formation_edit', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary'>
                        <i class='bi bi-pencil'  title='Editer'></i>
                    </a>

                    <a href='#' class='btn btn-sm m-1 btn-outline-danger' 
                        data-bs-toggle='modal' data-bs-target='#deleteModal{n.id}'>
                        <i class='bi bi-trash'  title='Supprimer'></i>
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
                                Supprimer : <strong> Le domaine {escape(n.nom)}</strong> ?
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('domaine_formation_delete', args=[n.id])}">
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


def export_domaine_formation_excel(request):
    #promotion_id = request.GET.get("promotion_id")
    filiere_id = request.GET.get("filiere_id")
    session_id = request.GET.get("session_id")

    qs = DomaineFormation.objects.all()

    # Application des mêmes filtres
    #if promotion_id:
    #    qs = qs.filter(promotion__nom=promotion_id)


    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Domaine_formation"

    # En-têtes
    headers = [
        "Nom", "Description",
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.nom,
            n.description,
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
    ] = 'attachment; filename=export_domaine_formation.xlsx'

    wb.save(response)
    return response


def formation(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    form = FormationForm()
    show_modal = False
    titre_modal = "Enregistrement"
    titre_btn = "Enregistrer"

    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Enregistrement effectué avec succès.")
            return redirect('formation')
        else:
            show_modal = True

    context = {
        'active':'6-2', 
        'form': form,
        'show_modal': show_modal,
        'utilisateur': utilisateur,
        'titre_modal': titre_modal,
        'titre_btn': titre_btn
    }
    return render(request, 'gestion/formation/formation.html', context)


def formation_edit(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    formation_edit = get_object_or_404(Formation, id=id)

    form = FormationForm(instance=formation_edit)

    show_modal = True
    info = ''
    titre_modal = "Mise à jour"
    titre_btn = "Mise à jour"

    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES, instance=formation_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('formation')
        
    context = {
        'active':'6-2',
        'form':form,
        'formation':formation,
        'show_modal':show_modal,
        'info':info,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
        'formation_edit':formation_edit
    }
    return render(request, 'gestion/formation/formation.html', context)


def formation_delete(request,id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    formation = get_object_or_404(Formation,id=id)
    formation.delete()
    return redirect('formation')


def formation_side(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)

    qs = Formation.objects.select_related(
        'domaine'
    ).order_by('-id')

    if search_value:
        qs = qs.filter(
            Q(nom__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(domaine__nom__icontains=search_value)
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        # Sécurisation image
        try:
            img_url = n.image.url
        except:
            img_url = '/static/default.png'
        
        video_url = n.video.url if n.video else ''

        video_html = f"""
        <div onclick="openVideoModal('{video_url}')"
            style="width:60px; height:60px; position:relative; border-radius:5px; overflow:hidden; background:#000; cursor:pointer;">
            
            <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:white;" title='cliquer pour voir la vidéo'>
                <i class="bi bi-play-circle-fill" style="font-size:24px;"></i>
            </div>
            
        </div>
        """ if video_url else "<span class='text-muted'>Aucune vidéo</span>"

        domaine_nom = n.domaine.nom if n.domaine and n.domaine.nom else "N/A"
        nom_court = escape((n.nom[:50] + '...') if len(n.nom) > 50 else n.nom)
        if not n.publiee:
            propose = f" par {escape(n.cree_par)}" if n.cree_par else ""
            statut_html = f"<div><span class='pill pill-or mt-1'><i class='bi bi-hourglass-split'></i> À valider{propose}</span></div>"
        else:
            statut_html = ""
        bouton_publier = f"""
                    <form method='post' action='{reverse('formation_publier', args=[n.id])}' class='d-inline'>
                        <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}'>
                        {"<button class='btn btn-sm m-1 btn-success' title='Valider et publier sur le site'><i class='bi bi-check2-circle'></i></button>"
                         if not n.publiee else
                         "<button class='btn btn-sm m-1 btn-outline-secondary' title='Retirer du site'><i class='bi bi-eye-slash'></i></button>"}
                    </form>"""

        data.append([
            f"""
            <img src="{img_url}" alt="image"
                style="width:60px; height:60px; object-fit:cover; border-radius:5px; cursor:pointer;"
                onclick="openImageModal('{img_url}')" title="cliquer pour voir l'image">
            """,
            video_html,
            nom_court + statut_html,
            escape((n.description[:50] + '...') if len(n.description) > 50 else n.description),
            escape((domaine_nom[:50] + '...') if len(domaine_nom) > 50 else domaine_nom),
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('sectionformation', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary' title='Gérer les sections'>
                        <i class='bi bi-file-earmark-plus'></i>
                    </a>
                </div>
            """,
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('ressourceformation', args=[n.id])}' 
                       class='btn btn-sm m-1 btn-outline-primary'>
                        <i class="bi bi-file-earmark-arrow-down-fill" title='Gérer les ressources'></i>
                    </a>
                </div>
            """,
            f"""
                <div class="d-flex justify-content-center">
                    {bouton_publier}
                    <a href='{reverse('formation_edit', args=[n.id])}' 
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
                                Supprimer : <strong> La formation {escape(n.nom)}</strong> ?   
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('formation_delete', args=[n.id])}">
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


def export_formation_excel(request):

    qs = Formation.objects.all()

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Formation"

    # En-têtes
    headers = [
        "Nom", "Description", "Domaine",
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.nom,
            n.description,
            n.domaine.nom,
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
    ] = 'attachment; filename=export_formation.xlsx'

    wb.save(response)
    return response


def sectionformation(request,formation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
    formation = get_object_or_404(Formation,id=formation_id)

    show_modal = False
    info = ''
    titre_modal = "Enregistrement"
    titre_btn = "Enregistrer"

    form = SectionFormationForm() 

            
    if request.method == 'POST' :
        form = SectionFormationForm(request.POST, request.FILES)
        if form.is_valid():
            sectionformation = form.save(commit=False)
            sectionformation.formation = formation
            sectionformation.save()
            messages.success(request, "Enregistrement effectué avec succès.")
            return redirect('sectionformation', formation_id)       
        else:
            show_modal = True
        
    context = {
        'active':'6-2',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'formation':formation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn
    }
    return render(request, 'gestion/section_formation/section_formation.html', context)


def sectionformation_edit(request,id,formation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    formation = get_object_or_404(Formation,id=formation_id)

    sectionformation_edit = get_object_or_404(SectionFormation, id=id)


    form = SectionFormationForm(instance=sectionformation_edit)

    show_modal = True
    info = ''
    titre_modal = "Mise à jour"
    titre_btn = "Mise à jour"

    if request.method == 'POST':
        form = SectionFormationForm(request.POST, request.FILES, instance=sectionformation_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('sectionformation', formation_id)
        
    context = {
        'active':'6-2',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'formation':formation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
        }
    return render(request, 'gestion/section_formation/section_formation.html', context)


def sectionformation_delete(request,id,formation_id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    formation = get_object_or_404(Formation,id=formation_id)
    sectionformation = get_object_or_404(SectionFormation,id=id)
    sectionformation.delete()
    return redirect('sectionformation', formation_id)


@csrf_exempt
def sectionformation_side(request, formation_id):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)

    formation = get_object_or_404(Formation,id=formation_id)
    qs = SectionFormation.objects.filter(formation=formation).order_by('id')
    # Query filtrable
    qs = qs.select_related('formation')

    if search_value:
        qs = qs.filter(
            Q(titre__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(formation__nom__icontains=search_value)
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        data.append([
            escape(n.titre),
            escape((n.contenu[:180] + '...') if len(n.contenu) > 180 else n.contenu),
            escape(n.formation.nom),
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('sectionformation_edit', args=[n.id, n.formation_id])}' 
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
                                Supprimer : <strong> La section {escape(n.titre)}</strong> ?   
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('sectionformation_delete', args=[n.id, n.formation_id])}">
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


def export_sectionformation_excel(request):

    qs = SectionFormation.objects.all()

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "SectionFormation"

    # En-têtes
    headers = [
        "Titre", "Contenu", "Formation",
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.titre,
            n.contenu,
            n.formation.nom,
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
    ] = 'attachment; filename=export_sectionformation.xlsx'

    wb.save(response)
    return response


#RESSOURCEFORMATION
def ressourceformation(request,formation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
    formation = get_object_or_404(Formation,id=formation_id)

    show_modal = False
    info = ''
    titre_modal = "Enregistrement"
    titre_btn = "Enregistrer"

    form = RessourceFormationForm() 

            
    if request.method == 'POST' :
        form = RessourceFormationForm(request.POST, request.FILES)
        if form.is_valid():
            ressourformation = form.save(commit=False)
            ressourformation.formation = formation
            ressourformation.save()
            messages.success(request, "Enregistrement effectué avec succès.")
            return redirect('ressourceformation', formation_id)       
        else:
            show_modal = True
        
    context = {
        'active':'6-2',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'formation':formation,
        'utilisateur':utilisateur,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn
    }
    return render(request, 'gestion/ressource_formation/ressource_formation.html', context)


def ressourceformation_edit(request,id,formation_id):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)

    formation = get_object_or_404(Formation,id=formation_id)

    ressourceformation_edit = get_object_or_404(RessourceFormation, id=id)


    form = RessourceFormationForm(instance=ressourceformation_edit)

    show_modal = True
    info = ''
    titre_modal = "Mise à jour"
    titre_btn = "Mise à jour"

    if request.method == 'POST':
        form = RessourceFormationForm(request.POST, request.FILES, instance=ressourceformation_edit)
        if form.is_valid():  
            form.save()
            messages.success(request, "Mise à jour effectuée avec succès")
            return redirect('ressourceformation', formation_id)
        
    context = {
        'active':'6-2',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'formation':formation,
        'utilisateur':utilisateur,
        'ressourceformation_edit':ressourceformation_edit,
        'titre_modal':titre_modal,
        'titre_btn':titre_btn,
        }
    return render(request, 'gestion/ressource_formation/ressource_formation.html', context)


def ressourceformation_delete(request,id,formation_id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    formation = get_object_or_404(Formation,id=formation_id)
    ressourceformation = get_object_or_404(RessourceFormation,id=id)
    ressourceformation.delete()
    return redirect('ressourceformation', formation_id)


@csrf_exempt
def ressource_formation_side(request, formation_id):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)
    formation = get_object_or_404(Formation, id=formation_id)

    qs = RessourceFormation.objects.filter(formation=formation).order_by('id')
    qs = qs.select_related('formation')

    if search_value:
        qs = qs.filter(
            Q(titre__icontains=search_value) |
            Q(description__icontains=search_value) |
            Q(formation__nom__icontains=search_value)
        )

    total = qs.count()
    filtered = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:

        pdf_url = n.pdf.url if n.pdf else ""
        video_url = n.video.url if n.video else ""

        video_url = n.video.url if n.video else ''

        video_html = f"""
        <div onclick="openVideoModal('{video_url}')"
            style="width:60px; height:60px; position:relative; border-radius:5px; overflow:hidden; background:#000; cursor:pointer;">
            
            <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:white;">
                <i class="bi bi-play-circle-fill" style="font-size:24px;"></i>
            </div>

        </div>
        """ if video_url else "<span class='text-muted'>Aucune vidéo</span>"

        data.append([
            escape(n.titre),
            escape(n.formation.nom),

            f"""
                <a href='{pdf_url}' target='_blank' class='text-danger fs-3'>
                    <i class='bi bi-file-earmark-pdf-fill'></i>
                </a>
            """ if pdf_url else "<span class='text-muted'>—</span>",

            video_html,

            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('ressourceformation_edit', args=[n.id, n.formation_id])}' 
                        class='btn btn-sm m-1 btn-outline-primary'>
                        <i class='bi bi-pencil'  title='Editer'></i>
                    </a>

                    <a href='#' class='btn btn-sm m-1 btn-outline-danger' 
                       data-bs-toggle='modal' data-bs-target='#deleteModal{n.id}'>
                        <i class='bi bi-trash'  title='Supprimer'></i>
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
                                Voulez-vous supprimer : <strong>{escape(n.titre)}</strong> ?
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('ressourceformation_delete', args=[n.id, n.formation_id])}">
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


def export_ressourceformation_excel(request):

    qs = RessourceFormation.objects.select_related('formation')

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "RessourceFormation"

    # En-têtes
    headers = [
        "Titre", "Description", "Formation"
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for n in qs:
        ws.append([
            n.titre,
            n.description,
            n.formation.nom,
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
    ] = 'attachment; filename=export_ressource_formation.xlsx'

    wb.save(response)
    return response


@require_POST
def formation_publier(request, id):
    """Valide (publie) ou retire du site une formation."""
    formation = get_object_or_404(Formation, id=id)
    formation.publiee = not formation.publiee
    formation.save(update_fields=['publiee'])
    if formation.publiee:
        messages.success(request, f"La formation « {formation.nom} » est publiée sur le site.")
    else:
        messages.success(request, f"La formation « {formation.nom} » est retirée du site.")
    suivant = request.POST.get('suivant') or ''
    return redirect(suivant if suivant.startswith('/') and not suivant.startswith('//') else 'formation')
