from django.test import TestCase, Client
from .forms import ContactForm, EditProfileForm, RegisterUserForm, AddPostForm
from .models import CustomUser 
from django.urls import reverse
from .models import CustomUser

# Create your tests here.

class ContactFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'sender': 'test@example.com',
            'cc_myself': True
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'subject': '',
            'message': '',
            'sender': 'invalid-email',
            'cc_myself': True
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)

class EditProfileFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_valid_form(self):
        data = {
            'username': 'newusername',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newemail@example.com',
        }
        form = EditProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'username': '',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
        }
        form = EditProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)

class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact')

    def test_get_contact_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_post_valid_contact_form(self):
        data = {
            'subject': 'Test Subject',
            'message': 'Test Message',
            'sender': 'test@example.com',
            'cc_myself': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful form submission
        self.assertRedirects(response, reverse('contact'))

    def test_post_invalid_contact_form(self):
        data = {
            'subject': '',
            'message': '',
            'sender': 'invalid-email',
            'cc_myself': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'subject', 'This field is required.')
        self.assertFormError(response, 'form', 'message', 'This field is required.')
        self.assertFormError(response, 'form', 'sender', 'Enter a valid email address.')

class EditProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('edit_profile')

    def test_get_edit_profile_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_post_valid_profile_form(self):
        data = {
            'username': 'newusername',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newemail@example.com',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful form submission
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'newemail@example.com')

    def test_post_invalid_profile_form(self):
        data = {
            'username': '',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')