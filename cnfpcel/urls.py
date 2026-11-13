"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from .views import espace_formateur as ef, formateurs as gf
urlpatterns = [
    
    path("",views.index,name="index"),
    path('page-indisponible/',views.page_indisponible,name='page_indisponible'),
    path('personnel-liste/',views.personnel_liste,name='personnel_liste'),
    #User
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name="logout"),
    path('profil-user/',views.profil_user,name='profil_user'),
    path('mot_de_passe_oublie/',views.mot_de_passe_oublie,name='mot_de_passe_oublie'),
    path('update_infos/',views.update_infos,name='update_infos'),
    path('update_password/',views.update_password,name='update_password'),
    #Gestion personnel
    path('gestion/',views.gestion,name='gestion'),
    path('gestion/personnel',views.personnel,name='personnel'),
    path('gestion/personnel_edit/<int:id>/',views.personnel_edit,name='personnel_edit'),
    path('gestion/personnel_delete/<int:id>/',views.personnel_delete,name='personnel_delete'),
    path('personnel_side',views.personnel_side,name='personnel_side'),
    #Lien des articles
    path('gestion/article',views.article,name='article'),
    path('article-edit/<int:id>',views.article_edit,name='article_edit'),
    path('article-delete/<int:id>',views.article_delete,name='article_delete'),
    path('article/paragraphe/<int:id>',views.paragraphe,name='paragraphe'),
    path('paragraphe-edit/<int:id>/<int:idp>/',views.paragraphe_edit,name='paragraphe_edit'),
    path('paragraphe-delete/<int:id>/<int:idp>/',views.paragraphe_delete,name='paragraphe_delete'),
    path('detail-article/<int:id>/',views.detail_article,name='detail_article'),
    path('article-liste/',views.article_liste,name='article_liste'),
    #Message contact
    path('gestion/lire-message-contact/',views.lire_message_contact,name='lire_message_contact'),
    path('gestion/supprimer-message-contact/<int:id>/',views.message_contact_delete,name='message_contact_delete'),
    path('gestion/supprimer-tous-message-contact/',views.supprimer_tous_les_messages_contact,name='supprimer_tous_les_messages_contact'),
    #Evenement
    path('gestion/evenement',views.evenement,name='evenement'),
    path('evenement-edit/<int:id>/',views.evenement_edit,name='evenement_edit'),
    path('evenement-delete/<int:id>/',views.evenement_delete,name='evenement_delete'),
    path('evenement-detail/<int:id>',views.evenement_detail,name='evenement_detail'),
    path('evenement-liste/',views.evenement_liste,name='evenement_liste'),

    #Domaine de formation
    path('gestion/domaine-formation/',views.domaine_formation,name='domaine_formation'),
    path('domaine_formation/',views.domaine_formation_side,name='domaine_formation_side'),
    path('gestion/domaine(formation-edit/<int:id>',views.domaine_formation_edit,name='domaine_formation_edit'),
    path('gestion/domaine-formation-delete/<int:id>',views.domaine_formation_delete,name='domaine_formation_delete'),
    path('export_domaine_formation_excel',views.export_domaine_formation_excel,name='export_domaine_formation_excel'),
    #Formation
    path('gestion/formation/',views.formation,name='formation'),
    path('formation_side',views.formation_side,name='formation_side'),
    path('gestion/formation-publier/<int:id>/',views.formation_publier,name='formation_publier'),
    path('gestion/formation-edit/<int:id>/',views.formation_edit,name='formation_edit'),
    path('gestion/formation-delete/<int:id>/',views.formation_delete,name='formation_delete'),
    path('export_formation_excel',views.export_formation_excel,name='export_formation_excel'),

    #Section formation
    path('gestion/sectionformation/<int:formation_id>',views.sectionformation,name='sectionformation'),
    path('gestion/sectionformation-delete/<int:id>/<int:formation_id>/',views.sectionformation_delete,name='sectionformation_delete'),
    path('gestion/sectionformation-edit/<int:id>/<int:formation_id>/',views.sectionformation_edit,name='sectionformation_edit'),
    path('section-formation/<int:formation_id>/side',views.sectionformation_side,name='sectionformation_side'),
    path('export_sectionformation_excel',views.export_sectionformation_excel,name='export_sectionformation_excel'),

    #ressource formation
    path('gestion/ressourceformation/<int:formation_id>',views.ressourceformation,name='ressourceformation'),
    path('gestion/ressourceformation-delete/<int:id>/<int:formation_id>/',views.ressourceformation_delete,name='ressourceformation_delete'),
    path('gestion/ressourceformation-edit/<int:id>/<int:formation_id>/',views.ressourceformation_edit,name='ressourceformation_edit'),
    path('ressource-formation/<int:formation_id>/side',views.ressource_formation_side,name='ressource_formation_side'),
    path('export_ressourceformation_excel',views.export_ressourceformation_excel,name='export_ressourceformation_excel'),

    path('liste-formation/<int:id>/',views.list_formation,name='list_formation'),
    path('liste-section-formation/<int:id>',views.list_section_formation,name='list_section_formation'),

    path('gestion/etudiant',views.etudiant,name='etudiant'),
    path('gestion/etudiant-accept/<int:id>/',views.accept_etudiant,name='accept_etudiant'),
    path('gestion/etudiant-delete/<int:id>/',views.etudiant_delete,name='etudiant_delete'),
    path('etudiant_side',views.etudiant_side,name='etudiant_side'),
    path('export_etudiant_excel',views.export_etudiant_excel,name='export_etudiant_excel'),
    path('formation-etudiant/',views.formation_etudiant,name='formation_etudiant'),
    path('gestion/etudiant-et-ses-formations/<int:id>/',views.etudiant_et_ses_formation,name='etudiant_et_ses_formation'),
    path('etudiant_et_ses_formation_side/<int:id>',views.etudiant_et_ses_formation_side,name='etudiant_et_ses_formation_side'),
    path('gestion/inscription-delete/<int:id>/',views.inscription_delete,name='inscription_delete'),

    path('gestion/galerie/',views.galerie,name='galerie'),
    path('gestion/galerie-edit/<int:id>/',views.galerie_edit,name='galerie_edit'),
    path('gestion/galerie-delete/<int:id>/',views.galerie_delete,name='galerie_delete'),
    path('galerie_side',views.galerie_side,name='galerie_side'),
    path('galerie-index',views.galerie_index,name='galerie_index'),

    #Evaluation
    path('gestion/evaluation/',views.evaluation,name='evaluation'),
    path('evaluation_side',views.evaluation_side,name='evaluation_side'),
    path('gestion/evaluation-edit/<int:id>/',views.evaluation_edit,name='evaluation_edit'),
    path('gestion/evaluation-delete/<int:id>/',views.evaluation_delete,name='evaluation_delete'),
    path('export_evaluation_excel',views.export_evaluation_excel,name='export_evaluation_excel'),
    #question evaluation
    path('gestion/question_evaluation/<int:evaluation_id>',views.question_evaluation,name='question_evaluation'),
    path('gestion/question_evaluation-delete/<int:id>/<int:evaluation_id>/',views.question_evaluation_delete,name='question_evaluation_delete'),
    path('gestion/question_evaluation-edit/<int:id>/<int:evaluation_id>/',views.question_evaluation_edit,name='question_evaluation_edit'),
    path('question-evaluation/<int:evaluation_id>/side',views.question_evaluation_side,name='question_evaluation_side'),
    path('export_question_evaluation_excel',views.export_question_evaluation_excel,name='export_question_evaluation_excel'),
    #reponse
    path('gestion/reponse-question/<int:question_id>/',views.reponse_question,name='reponse_question'),
    path('gestion/reponse-question-delete/<int:id>/<question_id>/',views.reponse_question_delete,name='reponse_question_delete'),
    path('gestion/reponse-question-edit/<int:id>/<question_id>/',views.reponse_question_edit,name='reponse_question_edit'),
    path('reponse-question/side/<int:question_id>/',views.reponse_question_side,name='reponse_question_side'),
    path('export_reponse_question_excel',views.export_reponse_question_excel,name='export_reponse_question_excel'),
    #passer evaluation
    path('evaluation/<int:evaluation_id>/passer/', views.passer_evaluation,name='passer_evaluation'),
    path('info-resultat-evaluation/<int:resultat_id>/', views.info_resultat_evaluation,name='info_resultat_evaluation'),
    #resultat evaluation
    path('gestion/resultat-evaluation/<int:evaluation_id>/',views.resultat_evaluation,name='resultat_evaluation'),
    path('gestion/resultat-evaluation-delete/<int:id>/<int:evaluation_id>/',views.resultat_evaluation_delete,name='resultat_evaluation_delete'),
    path('resultat_evaluation_side/<int:evaluation_id>/',views.resultat_evaluation_side,name='resultat_evaluation_side'),
    path('export_resultat_evaluaiton_excel',views.export_resultat_evaluaiton_excel,name='export_resultat_evaluaiton_excel'),
    path('temps-ecoule',views.temps_ecoule,name='temps_ecoule'),

    path('recherche-index/',views.recherche_index,name='recherche_index'),

    # Gestion des formateurs (personnel)
    path('gestion/formateur/', gf.formateur, name='formateur'),
    path('gestion/formateur/<int:id>/modifier/', gf.formateur_edit, name='formateur_edit'),
    path('gestion/formateur/<int:id>/supprimer/', gf.formateur_delete, name='formateur_delete'),
    path('gestion/formateur/<int:id>/acces/', gf.formateur_acces, name='formateur_acces'),
    path('gestion/formateur/<int:id>/activer/', gf.formateur_activer, name='formateur_activer'),

    # Espace formateur
    path('espace-formateur/', ef.espace_formateur, name='espace_formateur'),
    path('espace-formateur/formations/', ef.espace_formateur_formations, name='espace_formateur_formations'),
    path('espace-formateur/formation/ajouter/', ef.espace_formateur_formation_ajout, name='espace_formateur_formation_ajout'),
    path('espace-formateur/formation/<int:formation_id>/', ef.espace_formateur_formation, name='espace_formateur_formation'),
    path('espace-formateur/formation/<int:formation_id>/modifier/', ef.espace_formateur_formation_modif, name='espace_formateur_formation_modif'),
    path('espace-formateur/formation/<int:formation_id>/retirer/', ef.espace_formateur_formation_suppr, name='espace_formateur_formation_suppr'),
    path('espace-formateur/formation/<int:formation_id>/section/ajouter/', ef.espace_formateur_section_ajout, name='espace_formateur_section_ajout'),
    path('espace-formateur/section/<int:id>/modifier/', ef.espace_formateur_section_modif, name='espace_formateur_section_modif'),
    path('espace-formateur/section/<int:id>/supprimer/', ef.espace_formateur_section_suppr, name='espace_formateur_section_suppr'),
    path('espace-formateur/formation/<int:formation_id>/ressource/ajouter/', ef.espace_formateur_ressource_ajout, name='espace_formateur_ressource_ajout'),
    path('espace-formateur/ressource/<int:id>/modifier/', ef.espace_formateur_ressource_modif, name='espace_formateur_ressource_modif'),
    path('espace-formateur/ressource/<int:id>/supprimer/', ef.espace_formateur_ressource_suppr, name='espace_formateur_ressource_suppr'),
    path('espace-formateur/formation/<int:formation_id>/evaluation/ajouter/', ef.espace_formateur_evaluation_ajout, name='espace_formateur_evaluation_ajout'),
    path('espace-formateur/evaluation/<int:id>/', ef.espace_formateur_evaluation, name='espace_formateur_evaluation'),
    path('espace-formateur/evaluation/<int:id>/modifier/', ef.espace_formateur_evaluation_modif, name='espace_formateur_evaluation_modif'),
    path('espace-formateur/evaluation/<int:id>/supprimer/', ef.espace_formateur_evaluation_suppr, name='espace_formateur_evaluation_suppr'),
    path('espace-formateur/evaluation/<int:evaluation_id>/question/ajouter/', ef.espace_formateur_question_ajout, name='espace_formateur_question_ajout'),
    path('espace-formateur/question/<int:id>/modifier/', ef.espace_formateur_question_modif, name='espace_formateur_question_modif'),
    path('espace-formateur/question/<int:id>/supprimer/', ef.espace_formateur_question_suppr, name='espace_formateur_question_suppr'),
    path('espace-formateur/question/<int:question_id>/reponse/ajouter/', ef.espace_formateur_reponse_ajout, name='espace_formateur_reponse_ajout'),
    path('espace-formateur/reponse/<int:id>/modifier/', ef.espace_formateur_reponse_modif, name='espace_formateur_reponse_modif'),
    path('espace-formateur/reponse/<int:id>/supprimer/', ef.espace_formateur_reponse_suppr, name='espace_formateur_reponse_suppr'),
    path('espace-formateur/profil/', ef.espace_formateur_profil, name='espace_formateur_profil'),
]


