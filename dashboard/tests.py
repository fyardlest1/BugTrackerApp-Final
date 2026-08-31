# dashboard/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CompteSansEntrepriseTests(TestCase):
    def test_le_tableau_de_bord_ne_plante_pas(self):
        User = get_user_model()
        orphelin = User.objects.create_user(
            username='orphelin', password='Demo1234!')
        orphelin.company = None
        orphelin.save(update_fields=['company'])

        self.client.login(username='orphelin', password='Demo1234!')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aucune entreprise')
