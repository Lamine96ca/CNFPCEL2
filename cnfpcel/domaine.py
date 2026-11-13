"""Redirection vers le domaine principal du site (ex. cn.cnfpcel.com -> cnfpcel.gov.gn)."""
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class DomainePrincipalMiddleware:
    """
    Si `DOMAINE_PRINCIPAL` est défini, toute requête arrivant par une autre adresse
    (ancien domaine, www…) est redirigée (301) vers ce domaine, en gardant le chemin.
    Ainsi, c'est toujours le domaine principal qui s'affiche dans le navigateur.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.principal = (getattr(settings, 'DOMAINE_PRINCIPAL', '') or '').lower()

    def __call__(self, request):
        if self.principal:
            hote = request.get_host().split(':')[0].lower()
            if hote != self.principal and hote not in ('localhost', '127.0.0.1', '[::1]', 'testserver'):
                return HttpResponsePermanentRedirect(f"https://{self.principal}{request.get_full_path()}")
        return self.get_response(request)
