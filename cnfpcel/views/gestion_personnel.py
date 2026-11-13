"""Gestion du personnel."""
from ._commun import *  # noqa: F401,F403

__all__ = ['personnel', 'personnel_edit', 'personnel_delete', 'personnel_side']


def personnel(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)

            personnels_list = Personnel.objects.all()  # Tri par ID décroissant
            paginator = Paginator(personnels_list, 5)  
            page_number = request.GET.get('page')
            personnel = paginator.get_page(page_number)

            show_modal = False
            info = ''
            titre_modal = "Enregistrement"
            titre_btn = "Enregistrer"
            if request.method == 'POST' :
                form = PersonnelForm(request.POST, request.FILES)
                if form.is_valid():
                    email = form.cleaned_data.get('email')  #  champ email dans le formulaire
                    personnel = form.save(commit=False)
                    # Vérifie si l'utilisateur existe déjà
                    utilisateur, created = User.objects.get_or_create(
                        username=email,
                        defaults={
                            'first_name': personnel.prenom,
                            'last_name':personnel.nom,
                            'is_active':0,
                            'email': email,
                            'password': 'N@uv'  #  sera hashé plus bas
                        }
                    )

                    if created:
                        utilisateur.set_password('N@uv')  #  Hashage du mot de passe
                        utilisateur.save()

                    # Enregistrement du personnel
                    personnel = form.save(commit=False)
                    personnel.utilisateur = utilisateur
                    personnel.save()
                    messages.success(request,"Enregistrement effectué")
                    return redirect('personnel')
                else:
                    show_modal = True
                    context = {
                    'active':2,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'personnel':personnel,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/personnel/personnel.html', context)
                
            else:
                form = PersonnelForm() 
                context = {
                    'active':2,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'personnel':personnel,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
            return render(request, 'gestion/personnel/personnel.html', context)
        
    return redirect('login')


def personnel_edit(request, id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1:
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
            personnel_edit = get_object_or_404(Personnel, id=id)

            personnels_list = Personnel.objects.all().order_by('-id')
            paginator = Paginator(personnels_list, 5)
            page_number = request.GET.get('page')
            personnel = paginator.get_page(page_number)

            show_modal = True
            info = ''
            titre_modal = "Mise à jour"
            titre_btn = "Mettre à jour"
            if request.method == 'POST':
                form = PersonnelForm(request.POST, request.FILES, instance=personnel_edit)
                if form.is_valid():
                    # Vérifie si un utilisateur est déjà lié
                    email = form.cleaned_data.get('email')

                    # Vérifie si un utilisateur est déjà lié
                    utilisateur = getattr(personnel_edit, 'utilisateur', None)

                    if utilisateur:
                        # Met à jour l’email si changé
                        if utilisateur.email != email:
                            utilisateur.username = email
                            utilisateur.email = email
                            utilisateur.save()
                    else:
                        # Crée un utilisateur si aucun n’est lié
                        utilisateur = User.objects.create_user(
                            username=email,
                            email=email,
                            password='N@uv'
                        )
                        personnel_edit.utilisateur = utilisateur

                    show_modal=False
                    form.save()
                    messages.success(request, "Mise à jour effectuée")
                    return redirect('personnel')

                else:
                    context = {
                        'active':2,
                        'form': form,
                        'personnel': personnel,
                        'show_modal': show_modal,
                        'info':info,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/personnel/personnel.html', context)

            else:
                form = PersonnelForm(instance=personnel_edit)
                context = {
                    'active':2,
                    'form': form,
                    'personnel': personnel,
                    'show_modal': show_modal,
                    'info':info,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
                return render(request, 'gestion/personnel/personnel.html', context)
    return redirect('login')


def personnel_delete(request,id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1:
            utilisateur = get_object_or_404(Personnel,utilisateur=user)

            personnels_list = Personnel.objects.all().order_by('-id')
            paginator = Paginator(personnels_list, 5)
            page_number = request.GET.get('page')
            personnel = paginator.get_page(page_number)

            show_modal = False
            info = 'Suppression effectuée avec succès.'

            personnel_delete = Personnel.objects.get(id=id)
            personnel_delete.delete()
            messages.success(request,"Suppréssion effectuée")
            return redirect('personnel')

    return redirect('login')


@csrf_exempt
def personnel_side(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    utilisateur = get_object_or_404(Personnel, utilisateur=request.user)

    qs = Personnel.objects.filter(ne_pas_afficher=0)

    if search_value:
        qs = qs.filter(
            Q(telephone__icontains=search_value) |
            Q(nom__icontains=search_value) |
            Q(prenom__icontains=search_value) |
            Q(fonc__icontains=search_value) |
            Q(email__icontains=search_value)
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        # Sécurisation image
        try:
            img_url = n.photo.url
        except:
            img_url = '/static/default.png'

        data.append([
            f"""
                <img src='{img_url}'
                    alt='image'
                    style='width:60px; height:60px; object-fit:cover; border-radius:5px; cursor:pointer;'
                    data-bs-toggle='modal'
                    data-bs-target='#imageModal'
                    onclick="showImage('{img_url}')">
            """,

            f"{n.prenom} {n.nom}",
            n.fonc,
            n.telephone,
            n.email,
            n.bio,
            f"""
                <div class="d-flex justify-content-center">

                    <a href='{reverse('personnel_edit', args=[n.id])}' 
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
                                Supprimer : <strong> Le domaine {n.nom}</strong> ?
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('personnel_delete', args=[n.id])}">
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
