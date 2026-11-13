"""Connexion, profil et mot de passe des comptes de gestion."""
from ._commun import *  # noqa: F401,F403

__all__ = ['login_view', 'logout_view', 'profil_user', 'update_infos', 'update_password', 'mot_de_passe_oublie']


#GESTION DES UTILISATEUR
def login_view(request):
    """Connexion unique : chaque compte est redirigé vers son espace (gestion, formateur, participant)."""
    from ..roles import page_accueil, role_de
    if request.user.is_authenticated and role_de(request.user):
        return redirect(page_accueil(request.user))

    erreur = ""
    username = ""
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user is None:
            erreur = "Identifiant ou mot de passe incorrect."
        elif role_de(user) is None:
            erreur = "Ce compte n'est rattaché à aucun espace. Contactez l'administration."
        else:
            login(request, user)
            suivant = request.GET.get('next')
            if suivant and suivant.startswith('/') and not suivant.startswith('//'):
                return redirect(suivant)
            return redirect(page_accueil(user))

    return render(request, 'gestion/user/login.html', {'erreur': erreur, 'username': username})


def logout_view(request):
    logout(request)  
    return redirect('login')


def profil_user(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
            info=''
            erreur=''
            user = request.user
            personnel = get_object_or_404(Personnel, utilisateur=user)
            info = ''
            show_modal = False
            context = {
                'user':user,
                'utilisateur': utilisateur,
                'info':info,
                'erreur':erreur,
                'show_modal':show_modal
            }
            return render(request,'gestion/user/profil.html', context)
    
    return redirect('login')


def update_infos(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
            info=''
            erreur =''
            if request.method == 'POST':
                
                user = request.user
                personnel = get_object_or_404(Personnel,utilisateur=user)
                personnel.prenom = request.POST.get('prenom')
                personnel.nom = request.POST.get('nom')
                personnel.telephone=request.POST.get('telephone')
                personnel.email=request.POST.get('email')
                personnel.save()
                info = "Mise à jour effectuée"

                user.first_name = request.POST.get('prenom')
                user.last_name = request.POST.get('nom')
                user.email = request.POST.get('email')
                user.username = user.email  #  si tu veux que le login reste aligné
                user.save()

                show_modal = True
                context = {
                    'utilisateur': utilisateur,
                    'info':info,
                    'erreur':erreur,
                    'show_modal':False
                }
                return render(request,'gestion/user/profil.html', context)
            
            return redirect('profil_user')
    return redirect('login')


def update_password(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)

            info =''
            erreur = ''
            if request.method == 'POST':
                user = request.user
                old = request.POST.get('old_password')
                new = request.POST.get('new_password')
                confirm = request.POST.get('confirm_password')

                if not user.check_password(old):
                    erreur = "Mot de passe actuel incorrect."
                elif new != confirm:
                    erreur = "Les mots de passe ne correspondent pas."
                else:
                    user.set_password(new)
                    user.save()
                    update_session_auth_hash(request, user)
                    info = "Mot de passe mis à jour avec succès."
                
                context = {
                    'utilisateur':utilisateur,
                    'info':info,
                    'erreur':erreur
                }
                return render(request,'gestion/user/profil.html', context)
            return redirect('profil_user')
    return redirect('login')


def mot_de_passe_oublie(request):
    erreur = ''
    info = ''
    user =''
    if request.method == 'POST':
        email = request.POST.get('email')
        try:

            user = User.objects.get(email=email)

            nouveau_mdp = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            try:
                utilisateur = Personnel.objects.get(utilisateur=user)
            except Personnel.DoesNotExist:
                try:
                    utilisateur = Etudiant.objects.get(utilisateur=user)
                except Etudiant.DoesNotExist:
                    utilisateur = None
 
            message_html = render_to_string('gestion/user/reunitialisation.html', {
                'utilisateur': utilisateur,
                'nouveau_mdp': nouveau_mdp,
                'dommaine':domaine,
            })

            email_obj = EmailMultiAlternatives(
                subject='Votre nouveau mot de passe CNFPCEL',
                body='Voici votre nouveau mot de passe.',
                from_email=email_reponse,
                to=[email]
            )
            email_obj.attach_alternative(message_html, "text/html")
            email_obj.send()

            user.set_password(nouveau_mdp)
            user.save()

            info ="Votre mot de passe a été envoyé à votre adresse."

        except User.DoesNotExist:
            erreur = "Aucun compte ne correspond à cet e-mail."

    context={'erreur':erreur,
             'info':info,
             'user':user,
            }
    
    return render(request, 'gestion/user/mot_de_passe_oublie.html',context)
