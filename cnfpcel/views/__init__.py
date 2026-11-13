"""
Vues de l'application CNFPATEL, regroupées par thème.

Les URL importent `views.<nom>` : chaque module ré-exporte ses vues ici.
"""
from .comptes import *  # noqa: F401,F403
from .public import *  # noqa: F401,F403
from .espace_etudiant import *  # noqa: F401,F403
from .tableau_bord import *  # noqa: F401,F403
from .gestion_personnel import *  # noqa: F401,F403
from .articles import *  # noqa: F401,F403
from .messages_contact import *  # noqa: F401,F403
from .evenements import *  # noqa: F401,F403
from .formations import *  # noqa: F401,F403
from .participants import *  # noqa: F401,F403
from .gestion_galerie import *  # noqa: F401,F403
from .evaluations import *  # noqa: F401,F403
