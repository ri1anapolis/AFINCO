#from django.test import TestCase
#from django.urls import reverse
#
#from model_mommy import mommy
#from model_mommy.recipe import Recipe, foreign_key
#
#from .models import Depositos
#from .forms import DepositoCreateForm
#from .views import DepositoDetailView
#
#class DepositosTestModel(TestCase):
#
#    def test_model_create(self):
#        deposito = mommy.make('depositos.Depositos')
#        self.assertTrue(isinstance(deposito, Depositos))
#
#    def test_view_detail(self):
#        deposito = mommy.make('depositos.Depositos')
#        resp = self.client.get(reverse('deposito_detail', args=[deposito.id]))
#        print(f'deposito.id: {deposito.id}\nresp: {resp}')
#        self.assertEqual(resp.status_code, 200)
#        self.assertIn(deposito, resp.content)
