from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import Blog, Comment, CustomUser, Profile, Draft, generate_unique_slug
from taggit.forms import TagField  
from django import forms
from .models import Blog, Comment, CustomUser, Profile, Draft, Category,Announcement
from taggit.forms import TagField

class AddPostForm(forms.ModelForm):
    tags = TagField(label='Теги', required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Категорія не обрана"

    class Meta:
        model = Blog
        fields = ['title', 'slug', 'content', 'photo', 'video', 'status', 'cat', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
            'video': forms.FileInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 200:
            raise forms.ValidationError('Довжина перевищує 200 символів')
        return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = generate_unique_slug(instance.title)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(label="Ім'я", widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label='Прізвище', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-input'
        self.fields['password1'].widget.attrs['class'] = 'form-input'
        self.fields['password2'].widget.attrs['class'] = 'form-input'

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логін', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
        }

class EditProfileForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'avatar')

class DraftForm(forms.ModelForm):
    tags = TagField(label='Теги', required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Draft
        fields = ['title', 'content', 'status', 'photo', 'cat', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
        }



class AddAnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 200:
            raise forms.ValidationError('Довжина перевищує 200 символів')
        return title