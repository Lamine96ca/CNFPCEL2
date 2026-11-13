"""Imports et constantes communs à toutes les vues."""
from django.shortcuts import render,redirect, get_object_or_404
from ..forms import *
from ..models import *
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
import random
import string
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
import bleach
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
import pandas as pd
from datetime import datetime
from django.template.loader import get_template
from django.conf import settings
import os
from django.urls import reverse
from django.db.models import Avg

from io import BytesIO
from django.core.files.base import ContentFile
import base64
from openpyxl import load_workbook
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.templatetags.static import static

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.http import HttpResponse


# Balises autorisées dans les textes riches (bleach)
allowed_tags = ['strong', 'em', 'br','a', 'p', 'ul', 'li']
allowed_attrs = {
    'a': ['href', 'title', 'target']
}

# Adresse d'envoi et adresse publique du site (réglées dans le fichier .env)
email_reponse = settings.DEFAULT_FROM_EMAIL
domaine = settings.URL_PUBLIQUE

# Imports auparavant dispersés au milieu de l'ancien views.py
import json
from django.db import IntegrityError, transaction
from django.http import Http404
