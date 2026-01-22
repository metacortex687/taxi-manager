from django.test import TestCase, Client
from django.contrib.auth import get_user_model

class CSRFTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@mail.com", password="secret"
        )

    def test_csrf_protect(self):
        # 1. Для отправки надо, что бы было включено 'django.middleware.csrf.CsrfViewMiddleware'
        # 2. В получаемой get запросом форме было, {% csrf_token %}

        #self.client = Client(enforce_csrf_checks=True) #Этого не надо
        self.client = Client()
        #self.client.login(username='testuser', password='secret') #и этого не надо

        response = self.client.get('/site/test_csrf_protect/')

        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.client.cookies['csrftoken'].value) #не пустая строка
        self.assertEqual(type(self.client.cookies['csrftoken'].value),str) 


