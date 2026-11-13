# Mettre CNFPCEL en production

Le site Django est hébergé chez **o2switch** (cPanel, « Setup Python App »). Le domaine principal sera **`cnfpcel.gov.gn`**. L'ancienne adresse `cn.cnfpcel.com` restera active, mais redirigera automatiquement vers `cnfpcel.gov.gn` : c'est donc toujours `cnfpcel.gov.gn` qui s'affichera dans le navigateur.

## Situation actuelle (vérifiée le 13/11/2026)

| Élément | Hébergeur | État |
|---|---|---|
| DNS de `cnfpcel.gov.gn` | **SiteGround** (`ns1.siteground.net`, `ns2.siteground.net`) | pointe vers un serveur SiteGround (`35.215.107.76`) qui **redirige** vers `cn.cnfpcel.com` |
| E-mails `@cnfpcel.gov.gn` | **SiteGround** (MX `mx10/20/30.antispam.mailspamprotection.com`) | à **conserver tels quels** |
| Site Django | **o2switch** (`109.234.167.147`) | répond sur `cn.cnfpcel.com` |

**Objectif :** faire pointer `cnfpcel.gov.gn` directement vers o2switch, sans redirection, tout en laissant les e-mails chez SiteGround.

---

## Étape 1 — Sauvegarder la production actuelle

La base de production contient les vraies données (inscriptions, résultats…). **Elle ne doit pas être remplacée par la base locale.**

1. Dans o2switch, ouvrez cPanel puis **phpMyAdmin**, sélectionnez la base du site, puis **Exporter** (format SQL). Gardez le fichier.
2. Dans cPanel, ouvrez le **Gestionnaire de fichiers**, faites un clic droit sur le dossier de l'application et choisissez **Compresser** pour en garder une copie. C'est surtout le dossier `media/` qui compte : il contient les images, les PDF et les vidéos.

## Étape 2 — Ajouter `cnfpcel.gov.gn` chez o2switch

1. Dans cPanel, ouvrez **Domaines**, puis **Créer un domaine**, et saisissez `cnfpcel.gov.gn`. Décochez « partager la racine » si la case est proposée : le dossier public n'est pas utilisé par Django.
2. Faites de même pour `www.cnfpcel.gov.gn`, s'il n'est pas créé automatiquement.
3. Ouvrez **Setup Python App**, puis l'application existante (celle de `cn.cnfpcel.com`) :
   - si cPanel permet de l'associer à plusieurs domaines, ajoutez `cnfpcel.gov.gn` ;
   - sinon, mettez **Application URL** = `cnfpcel.gov.gn`, puis ajoutez `cn.cnfpcel.com` comme **alias** de `cnfpcel.gov.gn` (cPanel, puis **Domaines**).

   Dans les deux cas, les deux adresses doivent arriver sur la même application. Django se charge ensuite de rediriger vers `cnfpcel.gov.gn`.

## Étape 3 — Modifier le DNS chez SiteGround (Site Tools)

1. Dans SiteGround, ouvrez **Site Tools**, puis **Domaine**, puis **Redirections** : **supprimez la redirection** de `cnfpcel.gov.gn` vers `cn.cnfpcel.com`.
2. Toujours dans Site Tools, ouvrez **Domaine**, puis **Zone DNS** :

   | Type | Nom | Valeur | Action |
   |---|---|---|---|
   | **A** | `cnfpcel.gov.gn` | `109.234.167.147` | **modifier** (remplace `35.215.107.76`) |
   | **A** ou **CNAME** | `www` | `109.234.167.147` (A) ou `cnfpcel.gov.gn` (CNAME) | modifier |
   | **MX** | — | `mx10/20/30.antispam.mailspamprotection.com` | **ne pas toucher** |
   | **A** | `mail` | (valeur actuelle SiteGround) | **ne pas toucher** |
   | TXT (SPF, DKIM) | — | — | **ne pas toucher** |

   > `109.234.167.147` est la « Shared IP Address » du compte o2switch `vazi2419` (confirmée dans cPanel). Ne pas utiliser la « Last Login IP Address » : c'est l'adresse de votre propre connexion Internet.

3. Attendez la propagation, de quelques minutes à quelques heures. Pour vérifier, `nslookup cnfpcel.gov.gn` doit renvoyer `109.234.167.147`.

> Si la zone DNS de `cnfpcel.gov.gn` n'est pas modifiable chez SiteGround, demandez à celui qui gère le domaine `.gov.gn` d'appliquer ces enregistrements.

## Étape 4 — HTTPS chez o2switch

Dans cPanel, ouvrez **SSL/TLS Status**, puis lancez **AutoSSL** pour `cnfpcel.gov.gn` et `www.cnfpcel.gov.gn`. Attendez que le cadenas soit vert. Le DNS de l'étape 3 doit déjà pointer vers o2switch.

## Étape 5 — Mettre le nouveau code sur le serveur

Ouvrez cPanel, puis **Terminal**. Collez la commande d'activation affichée en haut de Setup Python App, du type `source /home/vazi2419/virtualenv/DOSSIER/3.11/bin/activate && cd /home/vazi2419/DOSSIER`.

**Première fois avec Git :**
```bash
# Clé de déploiement (une seule fois) ; à ajouter dans GitHub → CNFPCEL2 → Settings → Deploy keys (lecture seule)
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519 -C "cnfpcel@o2switch"
cat ~/.ssh/id_ed25519.pub

# Dans le dossier de l'application (media/ et les fichiers non suivis par Git sont conservés)
git init -b main
git remote add origin git@github.com:Lamine96ca/CNFPCEL2.git
git fetch origin
git checkout -f -B main --track origin/main
```

> Si le dépôt GitHub est **public**, la clé de déploiement est inutile : utilisez `https://github.com/Lamine96ca/CNFPCEL2.git`.

**Installer les dépendances :**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Étape 6 — Réglages de production (`config/local_settings.py`)

```bash
cp config/local_settings.example.py config/local_settings.py
chmod 600 config/local_settings.py
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Ouvrez `config/local_settings.py` dans l'éditeur de fichiers de cPanel et renseignez :

```python
SECRET_KEY = 'la-clé-générée-ci-dessus'
DEBUG = False
ALLOWED_HOSTS = ['cnfpcel.gov.gn', 'www.cnfpcel.gov.gn', 'cn.cnfpcel.com']
DOMAINE_PRINCIPAL = 'cnfpcel.gov.gn'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'COMPTE_base', 'USER': 'COMPTE_utilisateur', 'PASSWORD': '...',
        'HOST': 'localhost', 'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4', 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

# E-mails : la boîte noreply@cnfpcel.gov.gn est chez SiteGround
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.cnfpcel.gov.gn'   # ou le nom de serveur SMTP indiqué par SiteGround
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'noreply@cnfpcel.gov.gn'
EMAIL_HOST_PASSWORD = '...'
DEFAULT_FROM_EMAIL = 'CNFPCEL <noreply@cnfpcel.gov.gn>'
```

Reprenez les valeurs de base de données et d'e-mail de la configuration actuelle du serveur.

## Étape 7 — Mettre à jour la base, les fichiers statiques et redémarrer

```bash
python manage.py migrate            # ajoute les nouveautés (ex. publication des formations), sans perte de données
python manage.py collectstatic --noinput
python manage.py check --deploy
mkdir -p tmp && touch tmp/restart.txt
```

## Étape 8 — Vérifier

- `https://cnfpcel.gov.gn` affiche le site, avec le cadenas vert.
- `https://cn.cnfpcel.com/...` renvoie vers `https://cnfpcel.gov.gn/...`, et c'est `cnfpcel.gov.gn` qui reste dans la barre d'adresse.
- La connexion fonctionne pour la gestion, l'espace formateur et l'espace participant.
- Un e-mail part bien, par exemple avec « Mot de passe oublié ».
- En cas d'erreur, consultez `logs/erreurs.log` dans le dossier de l'application.

Quand tout fonctionne depuis quelques jours, activez HSTS : mettez `SECURE_HSTS_SECONDS = 31536000` dans `local_settings.py`, puis redémarrez.

---

## Mises à jour suivantes

```bash
source /home/vazi2419/virtualenv/DOSSIER/3.11/bin/activate && cd /home/vazi2419/DOSSIER
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

## En cas de problème

| Symptôme | Piste |
|---|---|
| « Bad Request (400) » | le domaine manque dans `ALLOWED_HOSTS` |
| Boucle de redirection | vérifiez que la redirection SiteGround est bien supprimée (étape 3.1) |
| CSS absent | relancez `collectstatic`, puis redémarrez |
| Erreur 500 | consultez `logs/erreurs.log` |
| E-mails non envoyés | vérifiez `EMAIL_HOST` / `EMAIL_PORT` / mot de passe et le nom SMTP fourni par SiteGround |
| `mysqlclient` ne s'installe pas | normal chez o2switch : `PyMySQL` est utilisé automatiquement |
