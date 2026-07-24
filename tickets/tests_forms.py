# tickets/tests_forms.py
from django.test import TestCase
from tickets.forms import CommentForm


class CommentFormTest(TestCase):
    def test_commentaire_vide_refuse(self):
        form = CommentForm(data={'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_commentaire_valide_accepte(self):
        form = CommentForm(data={'content': 'Bien vu, je corrige.'})
        self.assertTrue(form.is_valid())
