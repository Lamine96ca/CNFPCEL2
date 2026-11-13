"""
Réglages Django du site CNFPCEL.

Tout ce qui change d'une machine à l'autre (clé secrète, base, e-mails, domaine, mode debug)
se règle dans le fichier `.env` à la racine du projet. Ce fichier n'est JAMAIS envoyé sur Git :
partir du modèle `.env.exemple`.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Lecture du fichier .env
# ---------------------------------------------------------------------------
def _charger_env(fichier):
    """
    Une ligne NOM=valeur, # pour un commentaire. Une variable déjà définie dans
    l'environnement (ex. cPanel) n'est pas remplacée.
    """
    if not fichier.exists():
        return
    for ligne in fichier.read_text(encoding='utf-8').splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith('#') or '=' not in ligne:
            continue
        nom, valeur = ligne.split('=', 1)
        valeur = valeur.strip()
        if len(valeur) >= 2 and valeur[0] == valeur[-1] and valeur[0] in '"\'':
            valeur = valeur[1:-1]
        os.environ.setdefault(nom.strip(), valeur)


_charger_env(BASE_DIR / '.env')


def _env(nom, defaut=''):
    return os.environ.get(nom, defaut).strip()


def _oui(nom, defaut='0'):
    return _env(nom, defaut).lower() in ('1', 'true', 'oui', 'yes')


def _liste(nom):
    return [v.strip() for v in _env(nom).split(',') if v.strip()]


# ---------------------------------------------------------------------------
# Mode, clé secrète, domaines
# ---------------------------------------------------------------------------
DEBUG = _oui('CNFPCEL_DEBUG', '1')          # 1 en développement, 0 en production


def _cle_secrete():
    cle = _env('CNFPCEL_SECRET_KEY')
    if cle:
        return cle
    if not DEBUG:
        raise ImproperlyConfigured(
            "CNFPCEL_SECRET_KEY manque dans le fichier .env : le site ne démarre pas sans clé secrète en production."
        )
    # Développement sans .env : clé générée une fois et gardée dans config/cle_secrete.txt (non versionné)
    fichier = BASE_DIR / 'config' / 'cle_secrete.txt'
    if fichier.exists() and fichier.read_text(encoding='utf-8').strip():
        return fichier.read_text(encoding='utf-8').strip()
    from django.core.management.utils import get_random_secret_key
    cle = get_random_secret_key()
    fichier.write_text(cle, encoding='utf-8')
    return cle


SECRET_KEY = _cle_secrete()

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]'] + _liste('CNFPCEL_ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in _liste('CNFPCEL_ALLOWED_HOSTS')]

# Domaine principal : toute autre adresse du site (ex. cn.cnfpcel.com) y est redirigée
DOMAINE_PRINCIPAL = _env('CNFPCEL_DOMAINE_PRINCIPAL')

# Adresse publique du site, utilisée dans les liens des e-mails
URL_PUBLIQUE = _env('CNFPCEL_URL_PUBLIQUE', 'https://cnfpcel.gov.gn').rstrip('/')


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cnfpcel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'cnfpcel.domaine.DomainePrincipalMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cnfpcel.roles.AccesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cnfpcel.context_processors.espace',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Base de données MySQL
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _env('CNFPCEL_DB_NAME', 'cnfpcel'),
        'USER': _env('CNFPCEL_DB_USER', 'root'),
        'PASSWORD': _env('CNFPCEL_DB_PASSWORD'),
        'HOST': _env('CNFPCEL_DB_HOST', 'localhost'),
        'PORT': _env('CNFPCEL_DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
        # Connexions réutilisées quelques secondes en production (moins de reconnexions sous Passenger)
        'CONN_MAX_AGE': 0 if DEBUG else 60,
        'CONN_HEALTH_CHECKS': True,
    }
}


# ---------------------------------------------------------------------------
# Mots de passe, langue
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Fichiers statiques (WhiteNoise) et fichiers téléversés
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'          # rempli par « collectstatic »
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# E-mails : sans CNFPCEL_EMAIL_HOST, ils s'affichent dans la console (aucun envoi)
# ---------------------------------------------------------------------------
EMAIL_HOST = _env('CNFPCEL_EMAIL_HOST')
if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = int(_env('CNFPCEL_EMAIL_PORT', '465'))
    EMAIL_USE_SSL = _oui('CNFPCEL_EMAIL_SSL', '1')
    EMAIL_USE_TLS = not EMAIL_USE_SSL and _oui('CNFPCEL_EMAIL_TLS', '0')
    EMAIL_HOST_USER = _env('CNFPCEL_EMAIL_USER')
    EMAIL_HOST_PASSWORD = _env('CNFPCEL_EMAIL_PASSWORD')
    EMAIL_TIMEOUT = 20
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = _env('CNFPCEL_EMAIL_FROM', 'CNFPCEL <noreply@cnfpcel.gov.gn>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# ---------------------------------------------------------------------------
# Production (CNFPCEL_DEBUG=0) : HTTPS, cookies sécurisés, journal des erreurs
# ---------------------------------------------------------------------------
if not DEBUG:
    # o2switch / cPanel : le HTTPS est terminé par le serveur web, qui transmet X-Forwarded-Proto
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    # 0 au début ; 31536000 (1 an) une fois le HTTPS validé sur tous les domaines
    SECURE_HSTS_SECONDS = int(_env('CNFPCEL_HSTS_SECONDES', '0'))

    (BASE_DIR / 'logs').mkdir(exist_ok=True)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {'simple': {'format': '{asctime} {levelname} {name} : {message}', 'style': '{'}},
        'handlers': {
            'fichier': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs' / 'erreurs.log',
                'maxBytes': 5 * 1024 * 1024, 'backupCount': 5,
                'formatter': 'simple', 'level': 'WARNING', 'encoding': 'utf-8',
            },
        },
        'loggers': {'django': {'handlers': ['fichier'], 'level': 'WARNING', 'propagate': True}},
    }
