"""Filtres de gabarit CNFPATEL."""
import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Mise en forme simple autorisée dans les contenus saisis (formateurs, personnel)
BALISES = ['strong', 'b', 'em', 'i', 'u', 'br', 'p', 'ul', 'ol', 'li', 'a', 'h4', 'h5', 'h6', 'blockquote']
ATTRIBUTS = {'a': ['href', 'title', 'target', 'rel']}


@register.filter
def nettoyer(valeur):
    """Garde la mise en forme simple et supprime tout le reste (scripts, événements, styles)."""
    if not valeur:
        return ''
    propre = bleach.clean(str(valeur), tags=BALISES, attributes=ATTRIBUTS,
                          protocols=['http', 'https', 'mailto'], strip=True)
    return mark_safe(propre)
