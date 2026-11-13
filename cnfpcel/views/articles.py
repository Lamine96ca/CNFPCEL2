"""Gestion des articles et de leurs paragraphes."""
from ._commun import *  # noqa: F401,F403

__all__ = ['article', 'article_edit', 'article_delete', 'paragraphe', 'paragraphe_edit', 'paragraphe_delete']


def article(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)

            articletitre_list = TitreArticle.objects.all().order_by('-id')  # Tri par ID décroissant
            paginator = Paginator(articletitre_list, 5)  
            page_number = request.GET.get('page')
            titrearticle = paginator.get_page(page_number)

            show_modal = False
            info = ''
            titre_modal = "Enregistrement"
            titre_btn = "Enregistrer"
            if request.method == 'POST' :
                form = TitreArticleForm(request.POST, request.FILES)
                if form.is_valid():
                   
                   form.save()
                   messages.success(request, "Enregistrement effectué avec succès.")
                   return redirect('article')
                
                else:
                    show_modal = True
                    context = {
                        'active':3,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'titrearticle':titrearticle,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/article/article.html', context)
                
            else:
                form = TitreArticleForm() 
                context = {
                    'active':3,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'titrearticle':titrearticle,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
            return render(request, 'gestion/article/article.html', context)
        
    return redirect('login')


def article_edit(request, id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1:
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
    
            article_edit = get_object_or_404(TitreArticle, id=id)

            articletitre_list = TitreArticle.objects.all().order_by('-id')  # Tri par ID décroissant
            paginator = Paginator(articletitre_list, 5)  
            page_number = request.GET.get('page')
            titrearticle = paginator.get_page(page_number)

            show_modal = True
            info = ''
            titre_modal = "Mise à jour"
            titre_btn = "Mise à jour"
            if request.method == 'POST':
                form = TitreArticleForm(request.POST, request.FILES, instance=article_edit)
                if form.is_valid():

                    show_modal=False
                    form.save()
                    messages.success(request, "Mise à jour effectuée avec succès")
                    return redirect('article')
                else:
                    context = {
                        'active':3,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'titrearticle':titrearticle,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/article/article.html', context)

            else:
                form = TitreArticleForm(instance=article_edit)
                context = {
                    'active':3,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'titrearticle':titrearticle,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                    }
                return render(request, 'gestion/article/article.html', context)
    return redirect('login')


def article_delete(request,id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1:
            article = TitreArticle.objects.get(id=id)
            article.delete()
            messages.success(request,"Suppression effectuée avec succès.")
            return redirect('article')
    return redirect('login')


def paragraphe(request,id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)

            titrearticle = get_object_or_404(TitreArticle,id=id)
            titre = titrearticle.titre
            id_article = titrearticle.id
            parapgraphe_list = Paragraphe.objects.filter(titreArticle=id).order_by('-id')  # Tri par ID décroissant
            paginator = Paginator(parapgraphe_list, 5)  
            page_number = request.GET.get('page')
            paragraphe = paginator.get_page(page_number)

            show_modal = False
            info = '',
            titre_modal = "Enregistrement"
            titre_btn = "Enregistrer"
            
            if request.method == 'POST' :
                form = ParagrapheForm(request.POST, request.FILES)
                if form.is_valid():
                    paragraphe_nettoye = bleach.clean(form.cleaned_data['contenu'], tags=allowed_tags)
                    paragraphe = form.save(commit=False)
                    paragraphe.titreArticle = titrearticle
                    paragraphe.contenu = paragraphe_nettoye
                    paragraphe.save()

                    messages.success(request, "Enregistrement effectué avec succès.")
                    return redirect('paragraphe', id=id)
                
                else:
                    show_modal = True
                    context = {
                        'active':3,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'paragraphe':paragraphe,
                        'titre':titre,
                        'id_article':id_article,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/article/paragraphe.html', context)
                
            else:
                form = ParagrapheForm() 
                context = {
                    'active':3,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'paragraphe':paragraphe,
                    'titre':titre,
                    'id_article':id_article,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
            return render(request, 'gestion/article/paragraphe.html', context)
        
    return redirect('login')


def paragraphe_edit(request, id,idp):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)

            paragraphe_edit = get_object_or_404(Paragraphe,id=idp)

            titre = paragraphe_edit.titreArticle.titre
            id_article = paragraphe_edit.titreArticle.id
            parapgraphe_list = Paragraphe.objects.all().order_by('-id')  # Tri par ID décroissant
            paginator = Paginator(parapgraphe_list, 5)  
            page_number = request.GET.get('page')
            paragraphe = paginator.get_page(page_number)

            show_modal = True
            info = ''
            titre_modal = "Mise à jour"
            titre_btn = "Mise à jour"
            
            if request.method == 'POST' :
                form = ParagrapheForm(request.POST, request.FILES, instance=paragraphe_edit)
                if form.is_valid():
                    paragraphe_nettoye = bleach.clean(form.cleaned_data['contenu'], tags=allowed_tags)
                    paragraphe = form.save(commit=False)
                    paragraphe.contenu = paragraphe_nettoye
                    paragraphe.save()


                    messages.success(request, "Mise à jour effectuée avec succès.")
                    return redirect('paragraphe', id=id)
                
                else:
                    show_modal = True
                    context = {
                        'active':3,
                        'show_modal':show_modal,
                        'info':info,
                        'form':form,
                        'paragraphe':paragraphe,
                        'titre':titre,
                        'id_article':id_article,
                        'utilisateur':utilisateur,
                        'titre_modal':titre_modal,
                        'titre_btn':titre_btn
                    }
                    return render(request, 'gestion/article/paragraphe.html', context)
                
            else:
                form = ParagrapheForm(instance=paragraphe_edit) 
                context = {
                    'active':3,
                    'show_modal':show_modal,
                    'info':info,
                    'form':form,
                    'paragraphe':paragraphe,
                    'titre':titre,
                    'id_article':id_article,
                    'utilisateur':utilisateur,
                    'titre_modal':titre_modal,
                    'titre_btn':titre_btn
                }
            return render(request, 'gestion/article/paragraphe.html', context)
        
    return redirect('login')


def paragraphe_delete(request,id,idp):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            paragraphe = get_object_or_404(Paragraphe,id=idp)
            paragraphe.delete()
            messages.success(request,'Suppréssion effectuée avec succès.')
            return redirect('paragraphe',id)
    return redirect('login')
