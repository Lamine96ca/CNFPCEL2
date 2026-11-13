from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import (DispenseFormation, Etudiant, Evaluation, Formateur, Formation,
                     Inscription, Personnel, Question, Reponse, SectionFormation)


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u_perso = User.objects.create_user('admin@test.gn', 'admin@test.gn', 'mdp-test-123', first_name='Awa')
        Personnel.objects.create(prenom='Awa', nom='Admin', telephone='600', email='admin@test.gn',
                                 fonc='Directrice', utilisateur=cls.u_perso)

        cls.u_form = User.objects.create_user('form@test.gn', 'form@test.gn', 'mdp-test-123', first_name='Ibra')
        cls.formateur = Formateur.objects.create(prenom='Ibra', nom='Formateur', telephone='601',
                                                 email='form@test.gn', utilisateur=cls.u_form)

        cls.u_etu = User.objects.create_user('etu@test.gn', 'etu@test.gn', 'mdp-test-123')
        cls.etudiant = Etudiant.objects.create(prenom='Mariam', nom='Etu', email='etu@test.gn', utilisateur=cls.u_etu)

        cls.f1 = Formation.objects.create(nom='Gouvernance locale', description='d', duree='3 jours')
        cls.f2 = Formation.objects.create(nom='Finances publiques', description='d', duree='2 jours')
        DispenseFormation.objects.create(formateur=cls.formateur, formation=cls.f1)
        Inscription.objects.create(etudiant=cls.etudiant, formation=cls.f1, accepte=True)


class ConnexionTests(Base):
    def test_redirection_selon_le_role(self):
        attendu = {'admin@test.gn': '/gestion/', 'form@test.gn': '/espace-formateur/', 'etu@test.gn': '/formation-etudiant/'}
        for email, url in attendu.items():
            self.client.logout()
            r = self.client.post(reverse('login'), {'username': email, 'password': 'mdp-test-123'})
            self.assertRedirects(r, url, fetch_redirect_response=False, msg_prefix=email)

    def test_mauvais_mot_de_passe(self):
        r = self.client.post(reverse('login'), {'username': 'admin@test.gn', 'password': 'faux'})
        self.assertContains(r, 'incorrect')


class AccesTests(Base):
    def test_gestion_reservee_au_personnel(self):
        for user in (self.u_form, self.u_etu):
            self.client.force_login(user)
            for nom in ('gestion', 'formation', 'formateur', 'etudiant'):
                r = self.client.get(reverse(nom))
                self.assertEqual(r.status_code, 302, f"{user} -> {nom}")
                self.assertFalse(r['Location'].startswith('/gestion'))

    def test_gestion_anonyme_redirige_vers_connexion(self):
        r = self.client.get(reverse('gestion'))
        self.assertRedirects(r, reverse('login'), fetch_redirect_response=False)

    def test_espace_formateur_refuse_aux_autres(self):
        self.client.force_login(self.u_etu)
        r = self.client.get(reverse('espace_formateur'))
        self.assertEqual(r.status_code, 302)

    def test_personnel_voit_toutes_les_pages(self):
        self.client.force_login(self.u_perso)
        for nom in ('gestion', 'formation', 'formateur', 'etudiant', 'evaluation', 'article', 'personnel'):
            self.assertEqual(self.client.get(reverse(nom)).status_code, 200, nom)


class GestionFormateursTests(Base):
    def setUp(self):
        self.client.force_login(self.u_perso)

    def test_creation_formateur_avec_compte_et_formations(self):
        r = self.client.post(reverse('formateur'), {
            'prenom': 'Nouveau', 'nom': 'Formateur', 'telephone': '622', 'email': 'Nouveau@Test.gn',
            'bio': '', 'formations': [self.f1.id, self.f2.id],
        })
        self.assertRedirects(r, reverse('formateur'), fetch_redirect_response=False)
        f = Formateur.objects.get(email='nouveau@test.gn')
        self.assertEqual(f.utilisateur.username, 'nouveau@test.gn')
        self.assertEqual(f.formateur_dispenser.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_en_double_refuse(self):
        r = self.client.post(reverse('formateur'), {
            'prenom': 'X', 'nom': 'Y', 'telephone': '699', 'email': 'admin@test.gn'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Formateur.objects.filter(telephone='699').exists())

    def test_modification_synchronise_les_formations(self):
        self.client.post(reverse('formateur_edit', args=[self.formateur.id]), {
            'prenom': 'Ibra', 'nom': 'Formateur', 'telephone': '601', 'email': 'form@test.gn',
            'formations': [self.f2.id]})
        ids = set(self.formateur.formateur_dispenser.values_list('formation_id', flat=True))
        self.assertEqual(ids, {self.f2.id})

    def test_suppression(self):
        self.client.post(reverse('formateur_delete', args=[self.formateur.id]))
        self.assertFalse(Formateur.objects.filter(id=self.formateur.id).exists())
        self.assertFalse(User.objects.filter(username='form@test.gn').exists())


class EspaceFormateurTests(Base):
    def setUp(self):
        self.client.force_login(self.u_form)

    def test_pages_principales(self):
        for url in (reverse('espace_formateur'), reverse('espace_formateur_formations'),
                    reverse('espace_formateur_profil')):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for onglet in ('sections', 'ressources', 'evaluations', 'participants', 'resultats'):
            r = self.client.get(reverse('espace_formateur_formation', args=[self.f1.id]), {'onglet': onglet})
            self.assertEqual(r.status_code, 200, onglet)
        self.assertContains(self.client.get(reverse('espace_formateur_formation', args=[self.f1.id]),
                                            {'onglet': 'participants'}), 'Mariam')

    def test_formation_non_attribuee_inaccessible(self):
        r = self.client.get(reverse('espace_formateur_formation', args=[self.f2.id]))
        self.assertEqual(r.status_code, 404)
        r = self.client.post(reverse('espace_formateur_section_ajout', args=[self.f2.id]),
                             {'titre': 't', 'contenu': 'c'})
        self.assertEqual(r.status_code, 404)
        self.assertFalse(SectionFormation.objects.filter(formation=self.f2).exists())

    def test_section_crud(self):
        self.client.post(reverse('espace_formateur_section_ajout', args=[self.f1.id]),
                         {'titre': 'Introduction', 'contenu': 'Bienvenue'})
        s = SectionFormation.objects.get(formation=self.f1)
        self.client.post(reverse('espace_formateur_section_modif', args=[s.id]),
                         {'titre': 'Intro', 'contenu': 'Bienvenue'})
        s.refresh_from_db()
        self.assertEqual(s.titre, 'Intro')
        self.client.post(reverse('espace_formateur_section_suppr', args=[s.id]))
        self.assertFalse(SectionFormation.objects.filter(id=s.id).exists())

    def test_evaluation_questions_reponses(self):
        r = self.client.post(reverse('espace_formateur_evaluation_ajout', args=[self.f1.id]),
                             {'titre': 'Quiz 1', 'description': '', 'duree': 10, 'note_minimale': 60, 'actif': 'on'})
        ev = Evaluation.objects.get(titre='Quiz 1')
        self.assertEqual(ev.formation, self.f1)
        self.assertRedirects(r, reverse('espace_formateur_evaluation', args=[ev.id]), fetch_redirect_response=False)

        self.client.post(reverse('espace_formateur_question_ajout', args=[ev.id]), {
            'texte': 'Capitale ?', 'reponse_texte': ['Conakry', 'Kindia', '', ''], 'reponse_correcte': '0'})
        q = Question.objects.get(evaluation=ev)
        self.assertEqual(list(q.reponse_set.order_by('id').values_list('texte', 'correcte')),
                         [('Conakry', True), ('Kindia', False)])

        self.client.post(reverse('espace_formateur_reponse_ajout', args=[q.id]), {'texte': 'Labé'})
        self.assertEqual(Reponse.objects.filter(question=q).count(), 3)
        self.assertEqual(self.client.get(reverse('espace_formateur_evaluation', args=[ev.id])).status_code, 200)

    def test_evaluation_dune_autre_formation_inaccessible(self):
        ev = Evaluation.objects.create(formation=self.f2, titre='Autre', duree=5)
        self.assertEqual(self.client.get(reverse('espace_formateur_evaluation', args=[ev.id])).status_code, 404)
        self.client.post(reverse('espace_formateur_question_ajout', args=[ev.id]), {'texte': 'x'})
        self.assertFalse(Question.objects.filter(evaluation=ev).exists())


class PropositionFormationTests(Base):
    def proposer(self, nom='Gestion des archives'):
        self.client.force_login(self.u_form)
        return self.client.post(reverse('espace_formateur_formation_ajout'),
                                {'nom': nom, 'duree': '4 jours', 'description': 'Contenu'})

    def test_formateur_propose_une_formation_en_attente(self):
        r = self.proposer()
        f = Formation.objects.get(nom='Gestion des archives')
        self.assertRedirects(r, reverse('espace_formateur_formation', args=[f.id]), fetch_redirect_response=False)
        self.assertFalse(f.publiee)
        self.assertEqual(f.cree_par, self.formateur)
        self.assertTrue(DispenseFormation.objects.filter(formateur=self.formateur, formation=f).exists())

    def test_formation_en_attente_invisible_sur_le_site(self):
        self.proposer()
        f = Formation.objects.get(nom='Gestion des archives')
        self.client.logout()
        self.assertNotContains(self.client.get(reverse('list_formation', args=[0])), 'Gestion des archives')
        self.assertEqual(self.client.get(reverse('list_section_formation', args=[f.id])).status_code, 404)
        # Aperçu possible pour le formateur
        self.client.force_login(self.u_form)
        self.assertEqual(self.client.get(reverse('list_section_formation', args=[f.id])).status_code, 200)

    def test_administration_valide_et_publie(self):
        self.proposer()
        f = Formation.objects.get(nom='Gestion des archives')
        self.client.force_login(self.u_perso)
        self.assertContains(self.client.get(reverse('gestion')), 'Gestion des archives')
        self.client.post(reverse('formation_publier', args=[f.id]))
        f.refresh_from_db()
        self.assertTrue(f.publiee)
        self.client.logout()
        self.assertContains(self.client.get(reverse('list_formation', args=[0])), 'Gestion des archives')

    def test_formateur_ne_peut_pas_publier(self):
        self.proposer()
        f = Formation.objects.get(nom='Gestion des archives')
        self.client.post(reverse('formation_publier', args=[f.id]))
        f.refresh_from_db()
        self.assertFalse(f.publiee)

    def test_retrait_seulement_si_non_publiee(self):
        self.proposer()
        f = Formation.objects.get(nom='Gestion des archives')
        f.publiee = True
        f.save()
        self.client.post(reverse('espace_formateur_formation_suppr', args=[f.id]))
        self.assertTrue(Formation.objects.filter(id=f.id).exists())
        f.publiee = False
        f.save()
        self.client.post(reverse('espace_formateur_formation_suppr', args=[f.id]))
        self.assertFalse(Formation.objects.filter(id=f.id).exists())

    def test_modification_des_informations(self):
        self.client.force_login(self.u_form)
        self.client.post(reverse('espace_formateur_formation_modif', args=[self.f1.id]),
                         {'nom': 'Gouvernance locale', 'duree': '5 jours', 'description': 'Nouveau'})
        self.f1.refresh_from_db()
        self.assertEqual(self.f1.duree, '5 jours')
        # Formation non attribuée : refusée
        r = self.client.post(reverse('espace_formateur_formation_modif', args=[self.f2.id]),
                             {'nom': 'X', 'duree': '1', 'description': 'y'})
        self.assertEqual(r.status_code, 404)

    def test_liste_gestion_echappe_le_nom(self):
        self.proposer(nom='<script>alert(1)</script>')
        self.client.force_login(self.u_perso)
        r = self.client.get(reverse('formation_side'), {'draw': 1, 'start': 0, 'length': 10})
        self.assertNotIn('<script>', r.content.decode())


class ContenuFormateurSecuriseTests(Base):
    """Le contenu saisi par un formateur ne doit jamais exécuter de script, ni sur le site ni dans la gestion."""
    PIEGE = '<script>alert(1)</script><img src=x onerror=alert(2)>'

    def setUp(self):
        self.client.force_login(self.u_form)
        self.client.post(reverse('espace_formateur_section_ajout', args=[self.f1.id]),
                         {'titre': 'S ' + self.PIEGE, 'contenu': '<strong>Gras</strong> ' + self.PIEGE})
        self.client.post(reverse('espace_formateur_evaluation_ajout', args=[self.f1.id]),
                         {'titre': 'E ' + self.PIEGE, 'duree': 5, 'note_minimale': 50, 'actif': 'on'})
        self.ev = Evaluation.objects.get(formation=self.f1)
        self.client.post(reverse('espace_formateur_question_ajout', args=[self.ev.id]),
                         {'texte': 'Q ' + self.PIEGE, 'reponse_texte': ['R ' + self.PIEGE, 'Autre'], 'reponse_correcte': '0'})
        self.q = Question.objects.get(evaluation=self.ev)

    def assert_sain(self, r):
        html = r.content.decode()
        self.assertNotIn('<script>alert(1)', html)
        self.assertNotIn('<img src=x onerror', html)
        self.assertNotIn('<img src="x" onerror', html)

    def test_site_public(self):
        r = self.client.get(reverse('list_section_formation', args=[self.f1.id]))
        self.assertEqual(r.status_code, 200)
        self.assert_sain(r)
        self.assertContains(r, '<strong>Gras</strong>')   # la mise en forme simple est conservée

    def test_espace_formateur(self):
        self.assert_sain(self.client.get(reverse('espace_formateur_formation', args=[self.f1.id])))
        self.assert_sain(self.client.get(reverse('espace_formateur_evaluation', args=[self.ev.id])))

    def test_listes_de_gestion(self):
        self.client.force_login(self.u_perso)
        p = {'draw': 1, 'start': 0, 'length': 10}
        for url in (reverse('sectionformation_side', args=[self.f1.id]),
                    reverse('evaluation_side'),
                    reverse('question_evaluation_side', args=[self.ev.id]),
                    reverse('reponse_question_side', args=[self.q.id])):
            self.assert_sain(self.client.get(url, p))
