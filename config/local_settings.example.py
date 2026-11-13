"""
Modèle de réglages locaux. Copiez ce fichier en `local_settings.py`
(dans le même dossier) puis remplacez les valeurs. Ne versionnez jamais local_settings.py.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Générer une clé : python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
SECRET_KEY = 'remplacer-par-une-cle-secrete-longue-et-aleatoire'

# ---- Développement ----
DEBUG = True

# ---- Production (serveur) : décommentez et adaptez ----
# DEBUG = False
# ALLOWED_HOSTS = ['cnfpcel.gov.gn', 'www.cnfpcel.gov.gn', 'cn.cnfpcel.com']
# DOMAINE_PRINCIPAL = 'cnfpcel.gov.gn'      # les autres adresses y sont redirigées
# SECURE_HSTS_SECONDS = 0                   # 31536000 une fois le HTTPS validé partout

# Base de données (production chez o2switch : base et utilisateur créés dans cPanel)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'moncompte_cnfpcel', 'USER': 'moncompte_cnfpcel', 'PASSWORD': '...',
#         'HOST': 'localhost', 'PORT': '3306',
#         'OPTIONS': {'charset': 'utf8mb4', 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
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
