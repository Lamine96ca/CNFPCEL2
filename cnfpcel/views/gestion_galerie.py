"""Gestion de la galerie photos."""
from ._commun import *  # noqa: F401,F403

__all__ = ['galerie', 'galerie_edit', 'galerie_delete', 'galerie_side']


#GALERIE
def galerie(request) : 
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    

    show_modal = False
    info = ''

    form = GalerieForm() 
   
    if request.method == "POST":
        form = GalerieForm(request.POST, request.FILES)
        
        galerie = Galerie.objects.create(
            description=request.POST.get('description'),
            date_prise=request.POST.get("date_prise")
        )
        if galerie : 
            images = request.FILES.getlist("images")
            for img in images:
                GalerieImage.objects.create(
                    galerie=galerie,
                    image=img
                )
            messages.success(request,"Enregistrement effectué avec succès")
            return redirect("galerie")
        
 
    context = {
        'active':'7',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'utilisateur':utilisateur
    }

    return render(request, 'gestion/galerie/galerie.html', context)


def galerie_edit(request,id) : 
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
    galerie_edit = get_object_or_404(GalerieImage,id=id)


    form = GalerieForm(instance=galerie_edit) 

    show_modal = True
    info = ''
   
    if request.method == "POST":
        form = GalerieForm(request.POST, request.FILES, instance=galerie_edit)
        if form.is_valid():
            galerie = Galerie.objects.create(
                description=form.cleaned_data["description"],
                date_prise=form.cleaned_data["date_prise"]
            )

            images = request.FILES.getlist("images")
            for img in images:
                GalerieImage.objects.create(
                    galerie=galerie,
                    image=img
                )

            return redirect("galerie")
 
    context = {
        'active':'7',
        'show_modal':show_modal,
        'info':info,
        'form':form,
        'utilisateur':utilisateur
    }

    return render(request, 'gestion/galerie/galerie.html', context)


def galerie_delete(request,id):
    if not request.user.is_authenticated :
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    
    galerie = get_object_or_404(Galerie,id=id)
    galerie.delete()
    return redirect('galerie')


def galerie_side(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    qs = Galerie.objects.all().order_by('id')

    if search_value:
        qs = qs.filter(
            Q(description__icontains=search_value)
        )

    total = qs.count()
    filtered = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:

        images = list(n.images.all())
        image_urls = [img.image.url for img in images if img.image]

        thumbnails = ""

        if image_urls:
            json_images = json.dumps(image_urls) 

            for img_url in image_urls[:3]:
                thumbnails += f"""
                    <img src="{img_url}"
                        style="width:50px; height:50px; object-fit:cover; border-radius:5px; margin:2px; cursor:pointer;"
                        onclick='openGallery({json_images})'>
                """

            if len(image_urls) > 3:
                thumbnails += f"""
                    <span style="font-size:12px; font-weight:bold; margin-left:5px;">
                        +{len(image_urls) - 3}
                    </span>
        """

        data.append([
            n.date_prise,
            n.description,

            f"""
                <div class="d-flex flex-wrap justify-content-center align-items-center">
                    {thumbnails}
                </div>
            """,
            f"""
            <a href='#' class='btn btn-sm m-1 btn-outline-danger' 
                data-bs-toggle='modal' data-bs-target='#deleteModal{n.id}'>
                <i class='bi bi-trash' title='Supprimer'></i>
            </a>
            <div class='modal fade' id='deleteModal{n.id}' tabindex='-1'>
                    <div class='modal-dialog modal-dialog-centered'>
                        <div class='modal-content'>
                            <div class='modal-header bg-danger text-white'>
                                <h5 class='modal-title'>Confirmation</h5>
                                <button type='button' class='btn-close btn-close-white' data-bs-dismiss='modal'></button>
                            </div>
                            <div class='modal-body'>
                                Voulez-vous supprimer : <strong>{n.description}</strong> ?
                            </div>
                            <div class='modal-footer'>
                                <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Annuler</button>
                                <form method='post' action="{reverse('galerie_delete', args=[n.id])}">
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
