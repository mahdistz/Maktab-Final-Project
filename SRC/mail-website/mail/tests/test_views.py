from django.test import Client
from django.test import TestCase
from mail.forms import CreateMailForm
from mail.models import Email, Signature, Filter, Category
from user.models import Users
from django.urls import reverse


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

    def test_create_email(self):
        # log user in and user
        self.client.login(username='foofoo@mail.com', password='password')
        # create new email
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
        # response = self.client.post('/mail/create_new_email/', form_data)
        # self.assertEqual(response.status_code, 200)
        # get number of created email to be tested later
        num_of_emails = Email.objects.all().count()
        # get created email
        email = Email.objects.filter(sender=self.user, recipients=self.user2)
        # test form validation
        self.assertTrue(form.is_valid())
        # test if the email sender is the same logged-in user
        self.assertEqual(self.email.sender, self.user)
        # one email created, test if this is true
        self.assertEqual(num_of_emails, 1)

    def test_inbox_emails(self):
        # log user in and user
        self.client.login(username='aaaaaa@mail.com', password='password')

        response = self.client.get(path='/mail/inbox/')

        self.assertEqual(response.status_code, 302)

    def test_redirect_to_login_page_when_user_not_login(self):
        response1 = self.client.get(path='/mail/inbox/')
        response2 = self.client.get(path='/mail/sent/')
        response3 = self.client.get(path='/mail/draft/')
        response4 = self.client.get(path='/mail/archive/')
        response5 = self.client.get(path='/mail/categories/')
        response6 = self.client.get(path='/mail/trash/')
        response7 = self.client.get(path='/contacts/')
        response8 = self.client.get(path='/mail/signatures/')

        self.assertRedirects(response1, '/login/?next=/mail/inbox/', 302)
        self.assertRedirects(response2, '/login/?next=/mail/sent/', 302)
        self.assertRedirects(response3, '/login/?next=/mail/draft/', 302)
        self.assertRedirects(response4, '/login/?next=/mail/archive/', 302)
        self.assertRedirects(response5, '/login/?next=/mail/categories/', 302)
        self.assertRedirects(response6, '/login/?next=/mail/trash/', 302)
        self.assertRedirects(response7, '/login/?next=/contacts/', 302)
        self.assertRedirects(response8, '/login/?next=/mail/signatures/', 302)

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='aaaaaa@mail.com', password='password')
        response = self.client.get('/mail/inbox/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='aaaaaa@mail.com', password='password')
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 302)

    def test_signatures(self):
        signature = Signature.objects.create(owner=self.user)
        self.email.signature = signature

        num_signatures = Signature.objects.all().count()
        self.assertEqual(num_signatures, 1)

        self.client.delete('/mail/signature_delete/<int:pk>/', data={'pk': 1})

        num_signatures = Signature.objects.all().count()
        self.assertEqual(num_signatures, 1)

    def test_categories(self):
        category = Category.objects.create(owner=self.user, name='test_category')
        num_categories = Category.objects.all().count()
        self.assertEqual(num_categories, 1)

    def test_email_detail(self):
        self.client.login(username='aaaaaa@mail.com', password='password')
        email = Email.objects.create(sender=self.user, subject='hi',
                                     body='email body', is_sent=True)
        self.email.recipients.add(self.user2)
        self.email.save()
        response = self.client.get('/mail/email_detail/<int:pk>/', data={'pk': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mail/email_detail.html')

    def test_filter(self):
        category = Category.objects.create(owner=self.user, name='test_category')
        filter_obj = Filter.objects.create(owner=self.user2, from_user='foofoo@mail.com', label=category)
        filters_num = Filter.objects.all().count()
        self.assertEqual(filters_num, 1)
        self.assertEqual(filter_obj.label.name, 'test_category')

    def test_reply(self):
        pass

    def test_forward(self):
        pass
