"""Messages reçus via le formulaire de contact."""
from ._commun import *  # noqa: F401,F403

__all__ = ['lire_message_contact', 'message_contact_delete', 'supprimer_tous_les_messages_contact']


def lire_message_contact(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            utilisateur = get_object_or_404(Personnel,utilisateur=user)
            messages_contact = MessageContact.objects.all().order_by('-id')
            paginator = Paginator(messages_contact, 5)
            page_number = request.GET.get('page')
            message_contact = paginator.get_page(page_number)
            total_message = MessageContact.objects.all().count()
            total_message_non_lu = MessageContact.objects.filter(lu=0).count()
            for msg in messages_contact:
                if msg.lu == 0:
                    msg.lu = 1
                    msg.save()
            context = {
                'active':5,
                'message_contact':message_contact,
                'total_message':total_message,
                'total_message_non_lu':total_message_non_lu,
                'utilisateur':utilisateur
            }
            return render(request,'gestion/messagecontact/lire_messge_contact.html',context)
    return redirect('login')


def message_contact_delete(request,id):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            message_contact = get_object_or_404(MessageContact,id=id)
            message_contact.delete()
            messages.success(request,'Suppréssion effectuée avec succès.')
            return redirect('lire_message_contact')
    return redirect('login')


def supprimer_tous_les_messages_contact(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_active==1 :
            MessageContact.objects.all().delete()
            messages.success(request,'Tous les messages ont été supprimés avec succès.')
            return redirect('lire_message_contact')
    return redirect('login')
