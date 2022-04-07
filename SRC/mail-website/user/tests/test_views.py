from django.test import Client
from django.test import TestCase
from mail.models import Email
from user.models import Users


class ViewTest(TestCase):

    def setUp(self) -> None:
        # create an instance of django.test.Client class.
        self.client = Client()

        self.user = Users.objects.create_superuser(
            username='foofoo@mail.com',
            password='1X<ISRUkw+tuK',
        )
        self.user2 = Users.objects.create_user(
            username='aaaaaa@mail.com',
            password='1X<ISRUkw+tuK',
            email='example@gmail.com',
            phone='09121212345',
            verification='Email',
        )
        self.user.save()
        self.user2.save()

        self.email = Email.objects.create(sender=self.user, subject='hi',
                                          body='email body', is_sent=True)
        self.email.recipients.add(self.user2)
        self.email.save()

    def test_home_page(self):
        # send GET request.
        # request to the specified url with GET request method.
        response = self.client.get(path='http://127.0.0.1:8000/home/')
        self.assertEqual(response.status_code, 302)

    def test_login_use_empty_username_password(self):
        login_account_test_data = {'username': '', 'password': '', 'remember_me': True}
        # send POST request.
        response = self.client.post(path='/login/', data=login_account_test_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_login_username_or_password_not_correct(self):
        login_account_test_data = {'username': 'Admin', 'password': 'qqqqqq'}

        response = self.client.post(path='/login/', data=login_account_test_data)

        self.assertEqual(response.status_code, 200)

        self.assertIn(b'Please enter a correct username and password.'
                      b' Note that both fields may be case-sensitive.',
                      response.content)

    def test_login_success(self):
        login_account_test_data = {'username': 'Admin@mail.com', 'password': 'salam1234'}

        response = self.client.post(path='/login/', data=login_account_test_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('home.html')
