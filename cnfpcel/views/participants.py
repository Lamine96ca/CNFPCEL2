"""Gestion des participants et de leurs inscriptions."""
from ._commun import *  # noqa: F401,F403
from django.utils.html import escape

__all__ = ['etudiant', 'accept_etudiant', 'etudiant_delete', 'inscription_delete', 'etudiant_side', 'etudiant_et_ses_formation', 'etudiant_et_ses_formation_side', 'export_etudiant_excel']


def etudiant(request): 
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active : 
        return redirect('ligon')
    
    utilisateur = get_object_or_404(Personnel, utilisateur=user)
    
    context ={
        'active':'6-3',
        'utilisateur':utilisateur,
    }
    return render(request,'gestion/etudiant/etudiant.html',context)


def accept_etudiant(request, id):
    if not request.user.is_authenticated or not request.user.is_active:
        return redirect('login')

    inscription = get_object_or_404(Inscription, id=id)
    etudiant = inscription.etudiant

    nouveau_mdp = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    mot_de_passe_cree = False

    try:
        with transaction.atomic():
            # Crée ou récupère le compte Django
            etudiant_compte, created = User.objects.get_or_create(
                username=etudiant.email,
                defaults={
                    'first_name': etudiant.prenom,
                    'last_name': etudiant.nom,
                    'is_active': True,
                    'email': etudiant.email,
                }
            )

            # Si le compte est créé, on définit le mot de passe
            if created:
                etudiant_compte.set_password(nouveau_mdp)
                etudiant_compte.save()
                mot_de_passe_cree = True

            # Marque l'inscription comme acceptée
            inscription.accepte = True
            inscription.save()

            # Lie le compte Django à l'étudiant
            etudiant.utilisateur = etudiant_compte
            etudiant.save()

    except Exception as e:
        messages.error(request, f"Erreur lors de l'acceptation : {e}")
        return redirect('etudiant_et_ses_formation', etudiant.id)

    # Préparer et envoyer l'email
    try:
        message_html = render_to_string('gestion/etudiant/info_acceptation.html', {
            'inscription': inscription,
            'etudiant': etudiant,
            'nouveau_mdp': nouveau_mdp if mot_de_passe_cree else None,
            'dommaine': domaine,
        })

        email_obj = EmailMultiAlternatives(
            subject='CNFPCEL - Acceptation',
            body='Votre inscription a été acceptée.',
            from_email=email_reponse,
            to=[etudiant.email]
        )
        email_obj.attach_alternative(message_html, "text/html")
        email_obj.send()
    except Exception as e:
        messages.warning(request, f"L'inscription a été acceptée mais l'email n'a pas pu être envoyé : {e}")
        return redirect('etudiant_et_ses_formation', etudiant.id)

    messages.success(request, 'Inscription acceptée avec succès.')
    return redirect('etudiant_et_ses_formation', etudiant.id)


def etudiant_delete(request,id):
    if not request.user.is_authenticated :
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    etudiant = get_object_or_404(Etudiant,id=id)
    user = get_object_or_404(User,id=etudiant.utilisateur_id)
    try:
        message_html = render_to_string('gestion/etudiant/info_rejet.html', {
                    'etudiant': etudiant,
                    'dommaine':domaine,
                })

        email_obj = EmailMultiAlternatives(
            subject='CNFPCEL-Refus',
            body='Votre inscription a été refusée.',
            from_email=email_reponse,
            to=[etudiant.email]
        )
        email_obj.attach_alternative(message_html, "text/html")
        email_obj.send()

        etudiant.delete()
        user.delete()
        messages.success(request,'Inscription rejetée')
        return redirect('etudiant')
    except Exception as e:
        messages.error(request, f"La suppression effectuée mais l'e-mail n'a été envoyé : {e}")
        return redirect('etudiant')


def inscription_delete(request,id):
    if not request.user.is_authenticated :
        return redirect('login')
    user = request.user
    if not user.is_active :
        return redirect('login')
    inscription = get_object_or_404(Inscription,id=id)
    etudiant = inscription.etudiant
    
    try:
        message_html = render_to_string('gestion/etudiant/info_rejet.html', {
            'etudiant': etudiant,
            'inscription': inscription,
            'dommaine':domaine,
        })
        message_html = render_to_string('gestion/etudiant/info_rejet.html', {
                    'etudiant': etudiant,
                    'inscription': inscription,
                    'dommaine':domaine,
                })

        email_obj = EmailMultiAlternatives(
            subject='CNFPCEL-Refus',
            body='Votre inscription a été refusée.',
            from_email=email_reponse,
            to=[etudiant.email]
        )
        email_obj.attach_alternative(message_html, "text/html")
        email_obj.send()
    except Exception as e:
        messages.warning(request, f"L'inscription a été rejetée mais l'e-mail n'a été envoyé : {e}")

    inscription.delete()
    messages.success(request,'Inscription rejetée')
    return redirect('etudiant')


@csrf_exempt
def etudiant_side(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    qs = Etudiant.objects.all().order_by('-id')

    if search_value:
        qs = qs.filter(
            Q(nom__icontains=search_value) |
            Q(prenom__icontains=search_value) |
            Q(telephone__icontains=search_value) |
            Q(email__icontains=search_value)
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:

        # --- Icône du statut ---
       
        # --- Ligne du tableau ---
        data.append([
            escape(n.prenom),
            escape(n.nom),
            escape(n.telephone),
            escape(n.email),

            # Bouton acceptation + modal
            f"""
                <div class="d-flex justify-content-center">
                    <a href="{reverse('etudiant_et_ses_formation', args=[n.id])}" title="Accéder aux formations" class="btn btn-sm m-1 btn-info">
                        <i class="bi bi-eye text-white"></i>
                    </a>
                </div>

                <div class="modal fade" id="accepte{n.id}" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header text-white" style="background-color:#0077B6;">
                                <h5 class="modal-title">Acceptation</h5>
                                <button type="button" class="btn-close btn-close-white"
                                    data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                Voulez-vous accepter l'inscription de 
                                <strong>{escape(n.prenom)} {escape(n.nom)}</strong> ?
                            </div>
                            <div class="modal-footer">
                                <form method="post" action="{reverse('etudiant_et_ses_formation', args=[n.id])}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                    <button class="btn btn-success">Oui, accepter</button>
                                </form>
                                <form method="post" action="{reverse('etudiant_delete', args=[n.id])}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                    <button class="btn btn-danger">Non, refuser</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """,

            # Bouton suppression + modal
            f"""
                <div class="d-flex justify-content-center">
                    <a href="#" class="btn btn-sm m-1 btn-outline-danger"
                        data-bs-toggle="modal" data-bs-target="#deleteModal{n.id}" title="Supprimer">
                        <i class="bi bi-trash"></i>
                    </a>
                </div>

                <div class="modal fade" id="deleteModal{n.id}" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">Confirmation</h5>
                                <button type="button" class="btn-close btn-close-white"
                                    data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                Supprimer l’étudiant :
                                <strong>{escape(n.prenom)} {escape(n.nom)}</strong> ?
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary"
                                    data-bs-dismiss="modal">Annuler</button>

                                <form method="post" action="{reverse('etudiant_delete', args=[n.id])}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                    <button class="btn btn-danger">Oui, supprimer</button>
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


def etudiant_et_ses_formation(request,id):
    if not request.user.is_authenticated : 
        return redirect('login')
    user = request.user
    if not user.is_active : 
        return redirect('ligon')
    
    utilisateur = get_object_or_404(Personnel, utilisateur=user)

    etudiant = get_object_or_404(Etudiant,id=id)
    
    context ={
        'active':'6-3',
        'utilisateur':utilisateur,
        'etudiant':etudiant,
    }
    return render(request,'gestion/etudiant/etudiant_et_ses_formation.html',context)


@csrf_exempt
def etudiant_et_ses_formation_side(request, id):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "")

    
    etudiant = get_object_or_404(Etudiant,id=id)
    qs = Inscription.objects.filter(etudiant=etudiant).order_by('-id').select_related(
        'etudiant'
    )

    if search_value:
        qs = qs.filter(
            Q(formation__nom__icontains=search_value) 
        )

    total = qs.count()
    qs = qs[start:start + length]

    csrf_token = get_token(request)
    data = []

    for n in qs:
        icone = "<i class='bi bi-check-circle text-white' title='Accepté'></i>" if n.accepte else "<i class='bi bi-hourglass-split text-white' title='En attente'></i>"
        data.append([
            escape(n.formation.nom),
            # Bouton acceptation + modal
            f"""
                <div class="d-flex justify-content-center">
                    <a href="" class="btn btn-sm m-1 btn-success"
                        data-bs-toggle="modal" data-bs-target="#accepte{n.id}">
                        {icone}
                    </a>
                </div>

                <div class="modal fade" id="accepte{n.id}" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header text-white" style="background-color:#0077B6;">
                                <h5 class="modal-title">Acceptation</h5>
                                <button type="button" class="btn-close btn-close-white"
                                    data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                Voulez-vous accepter l'inscription à la formation 
                                <strong>{escape(n.formation.nom)} </strong> ?
                            </div>
                            <div class="modal-footer">
                                <form method="post" action="{reverse('accept_etudiant', args=[n.id])}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                    <button class="btn btn-success">Oui, accepter</button>
                                </form>
                                <form method="post" action="{reverse('etudiant_delete', args=[n.id])}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                    <button class="btn btn-danger">Non, refuser</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            """,

            # Bouton suppression + modal
            f"""
                <div class="d-flex justify-content-center">
                    <a href="#" class="btn btn-sm m-1 btn-outline-danger"
                        data-bs-toggle="modal" data-bs-target="#deleteModal{n.id}">
                        <i class="bi bi-trash"></i>
                    </a>
                </div>

                <div class="modal fade" id="deleteModal{n.id}" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header bg-danger text-white">
                                <h5 class="modal-title">Confirmation</h5>
                                <button type="button" class="btn-close btn-close-white"
                                    data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                Retirer l'inscription en formation :
                                <strong>{escape(n.formation.nom)}</strong> ?
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary"
                                    data-bs-dismiss="modal">Annuler</button>

                                <form method="post" action="{reverse('inscription_delete', args=[n.id])}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                    <button class="btn btn-danger">Oui, supprimer</button>
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


def export_etudiant_excel(request):
    # Une ligne par inscription (un participant peut suivre plusieurs formations)
    qs = (Inscription.objects.select_related('etudiant', 'formation')
          .order_by('etudiant__nom', 'etudiant__prenom', 'formation__nom'))

    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Participant"

    # En-têtes
    headers = [
        "Prénom", "Nom", "Téléphone", "E-mail", "Formation", "Statut", "Date d'inscription"
    ]

    header_font = Font(bold=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Lignes du tableau
    for i in qs:
        ws.append([
            i.etudiant.prenom,
            i.etudiant.nom,
            i.etudiant.telephone,
            i.etudiant.email,
            i.formation.nom,
            "Acceptée" if i.accepte else "En attente",
            timezone.localtime(i.date_inscription).strftime("%d/%m/%Y"),
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
    ] = 'attachment; filename=export_participant.xlsx'

    wb.save(response)
    return response
