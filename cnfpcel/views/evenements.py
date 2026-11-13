"""Gestion des événements."""
from ._commun import *  # noqa: F401,F403

__all__ = ['evenement', 'evenement_edit', 'evenement_delete']


def evenement(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
            
            evenement_list = Evenement.objects.all().order_by('-id')  # Tri par ID décroissant
            paginator = Paginator(evenement_list, 5)  
            page_number = request.GET.get('page')
            evenement = paginator.get_page(page_number)

            show_modal = False
            info = ''
            titre_modal = "Enregistrement"
            titre_btn = "Enregistrer"
            
            if request.method == 'POST' :
                form = EvenementForm(request.POST, request.FILES)
                if form.is_valid():
                    description_nettoye = bleach.clean(request.POST.get('description'), tags=allowed_tags)
                    ajout_evenement= form.save(commit=False)
                    ajout_evenement.description = description_nettoye
                    ajout_evenement.save()

                    messages.success(request, "Enregistrement effectué avec succès.")
                    return redirect('evenement')
                
                else:
                    show_modal = True
                    context = {
                        'active':4,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'evenement':evenement,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/evenement/evenement.html', context)
                
            else:
                form = EvenementForm() 
                context = {
                    'active':4,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'evenement':evenement,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
            return render(request, 'gestion/evenement/evenement.html', context)
        
    return redirect('login')


def evenement_edit(request, id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1:
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
            evenement_edit = get_object_or_404(Evenement, id=id)

            evenement_list = Evenement.objects.all().order_by('-id')  # Tri par ID décroissant
            paginator = Paginator(evenement_list, 5)
            page_number = request.GET.get('page')
            evenement = paginator.get_page(page_number)

            show_modal = True
            info = ''
            titre_modal = "Mise à jour"
            titre_btn = "Mettre à jour"

            if request.method == 'POST':
                form = EvenementForm(request.POST, request.FILES, instance=evenement_edit)
                if form.is_valid():
                   
                   description_nettoye = bleach.clean(request.POST.get('description'), tags=allowed_tags)
                   maj_evenement= form.save(commit=False)
                   maj_evenement.description = description_nettoye
                   maj_evenement.save()

                   messages.success(request, "Mise à jour effectuée avec succès")
                   return redirect('evenement')
                else:
                    context = {
                        'active':4,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'evenement':evenement,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                        }
                    return render(request, 'gestion/evenement/evenement.html', context)

            else:
                form = EvenementForm(instance=evenement_edit)
                context = {
                    'active':4,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'evenement':evenement,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                    }
                return render(request, 'gestion/evenement/evenement.html', context)
    return redirect('login')


def evenement_delete(request,id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1:
            evenement = get_object_or_404(Evenement,id=id)
            evenement.delete()
            messages.success(request,"Suppression effectuée avec succès.")
            return redirect('evenement')
    return redirect('login')
