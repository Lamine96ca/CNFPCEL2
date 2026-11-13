"""
Modèle de réglages locaux. Copiez ce fichier en `local_settings.py`
(dans le même dossier) puis remplacez les valeurs. Ne versionnez jamais local_settings.py.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Générer une clé : python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
SECRET_KEY = 'remplacer-par-une-cle-secrete-longue-et-aleatoire'

DEBUG = True
# ALLOWED_HOSTS = ['cnfpcel.gov.gn', 'www.cnfpcel.gov.gn']

# Base de données (si différente de config/settings.py)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'cnfpcel', 'USER': 'root', 'PASSWORD': '',
#         'HOST': 'localhost', 'PORT': '3306',
#     }
# }

# Courriel — développement (serveur SMTP local sur le port 1025)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'CNFPCEL <noreply@cnfpcel.gov.gn>'

# Courriel — production
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.cnfpcel.gov.gn'
# EMAIL_PORT = 465
# EMAIL_USE_SSL = True
# EMAIL_USE_TLS = False
# EMAIL_HOST_USER = 'noreply@cnfpcel.gov.gn'
# EMAIL_HOST_PASSWORD = '...'
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
