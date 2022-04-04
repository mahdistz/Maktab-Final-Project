from django.test import Client
from django.test import TestCase
from django.urls import reverse
from user.models import Users
from mail.forms import CreateMailForm
from mail.models import Email


class ViewTest(TestCase):

    def setUp(self) -> None:
        # create an instance of django.test.Client class.
        self.client = Client()

        self.user = Users.objects.create_superuser(
            username='foofoo@mail.com',
            password='password',
        )
        self.user2 = Users.objects.create(
            username='aaaaaa@mail.com',
            password='password',
            email='example@gmail.com',
            phone='09121212345',
            verification='Email',
        )
        self.email = Email.objects.create(sender=self.user, subject='hi',
                                          body='email body', is_sent=True)
        self.email.recipients.add(self.user2)

    def test_home_page(self):
        print('******************test_home_page()**********************')
        # send GET request.
        # request to the specified url with GET request method.
        response = self.client.get(path='http://127.0.0.1:8000/home/')
        self.assertEqual(response.status_code, 302)

    def test_login_use_empty_username_password(self):
        print('******************test_login_use_empty_username_password()**********************')

        login_account_test_data = {'username': '', 'password': '', 'remember_me': True}

        # send POST request.
        response = self.client.post(path='/login/', data=login_account_test_data)

        self.assertEqual(response.status_code, 200)

        # self.assertIn(b'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', response.content)

        # self.assertIn(b"Your password can’t be too similar to your other personal information."
        #               b"Your password must contain at least 8 characters."
        #               b"Your password can’t be a commonly used password."
        #               b"Your password can’t be entirely numeric.", response.content)

    def test_login_username_or_password_not_correct(self):
        print('******************test_login_username_or_password_not_correct()**********************')

        login_account_test_data = {'username': 'Admin', 'password': 'qqqqqq'}

        response = self.client.post(path='/login/', data=login_account_test_data)

        print('Response status code : ' + str(response.status_code))

        self.assertEqual(response.status_code, 200)

        self.assertIn(b'Please enter a correct username and password.'
                      b' Note that both fields may be case-sensitive.',
                      response.content)

    def test_login_success(self):
        print('******************test_login_success()**********************')

        login_account_test_data = {'username': 'Admin', 'password': 'Admin'}

        response = self.client.post(path='/login/', data=login_account_test_data)

        print('Response status code : ' + str(response.status_code))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed('home.html')

    def test_create_email(self):
        # create update and delete a blog
        # log user in and user
        self.client.login(username='foofoo@mail.com', password='password')

        # create new blog
        # expected date from the user, you can put invalid data to test from validation
        form_data = {
            'sender': self.user,
            'subject': 'hi',
            'recipients': 'aaaaaa@mail.com',
            'body': 'email body',
        }

        form = CreateMailForm(data=form_data)  # create form instance

        """
        simulate post request with self.client.post
        /mail/create_new_email/ is the url associated with create_email view
        """
        response = self.client.post('/mail/create_new_email/', form_data)
        print(response.status_code)
        # get number of created email to be tested later
        num_of_emails = Email.objects.all().count()
        # get created email
        email = Email.objects.filter(sender=self.user, recipients=self.user2)
        print(email)
        # test form validation
        self.assertTrue(form.is_valid())
        # test if the email sender is the same logged-in user
        self.assertEqual(self.email.sender, self.user)
        # one email created, test if this is true
        self.assertEqual(num_of_emails, 1)

