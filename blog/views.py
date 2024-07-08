from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.mail import send_mail, BadHeaderError
from .forms import ContactForm, AddPostForm, RegisterUserForm, LoginUserForm, CommentForm, EditProfileForm
from .models import *
from .utils import menu
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.dispatch import receiver
from django.db.models.signals import post_save
from .utils import send_new_article_notification  
from django.contrib.auth import logout
from django.contrib.auth import login
from .forms import *
from django.utils.text import slugify
from .models import Blog, Draft  
from taggit.models import Tag  

class BlogHome(ListView):
    model = Blog
    template_name = 'index.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Головна сторінка"}
        context.update(c_def)
        context.update(menu(self.request))
        return context

    def get_queryset(self):
        return Blog.objects.filter(status='published').select_related('cat')
    
def about(request):
    contact_list = Blog.objects.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'about.html', {'page_obj': page_obj, 'menu': menu(request), 'title': 'Про сайт'})


class AddPage(CreateView):
    model = Blog
    form_class = AddPostForm
    template_name = 'addpage.html'
    success_url = reverse_lazy('home') 

    def form_valid(self, form):
        form.instance.author = self.request.user
        if 'save_draft' in self.request.POST:
            form.instance.status = 'draft'
        else:
            form.instance.status = 'published'
        response = super().form_valid(form)
        self.object.tags.set(*self.request.POST.get('tags', '').split(','))  
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_drafts = Blog.objects.filter(author=self.request.user, status='draft')
        if user_drafts.exists():
            context['drafts'] = user_drafts
        context['title'] = 'Додати сторінку'
        return context
    
@login_required
def save_draft(request, pk=None):
    if pk:
        draft = get_object_or_404(Blog, pk=pk, author=request.user, status='draft')
        form = AddPostForm(request.POST or None, request.FILES or None, instance=draft)
    else:
        form = AddPostForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            draft = form.save(commit=False)
            draft.author = request.user
            draft.status = 'draft'
            draft.save()
            return redirect('drafts')  

    user_drafts = Blog.objects.filter(author=request.user, status='draft')
    return render(request, 'drafts.html', {'form': form, 'drafts': user_drafts, 'title': 'Чернетки'})
  

def generate_unique_slug(title):
    slug = slugify(title)
    counter = 1
    while Blog.objects.filter(slug=slug).exists():
        slug = f'{slug}-{counter}'
        counter += 1
    return slug

def generate_unique_slug(title):
    slug = slugify(title)
    counter = 1
    while Blog.objects.filter(slug=slug).exists():
        slug = f'{slug}-{counter}'
        counter += 1
    return slug

def generate_unique_slug(title):
    slug = slugify(title)
    counter = 1
    while Blog.objects.filter(slug=slug).exists():
        slug = f'{slug}-{counter}'
        counter += 1
    return slug

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']

            recipients = ['admin@example.com']
            if cc_myself:
                recipients.append(sender)

            try:
                send_mail(subject, message, sender, recipients)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'menu': menu(request), 'title': 'Зворотній зв\'язок'})

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('login')

class ShowPost(DetailView):
    model = Blog
    template_name = 'post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('user')
        context['form'] = CommentForm()
        context['tags'] = self.object.tags.all() 
        return context
    
class WomenCategory(ListView):
    model = Blog
    template_name = 'index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Blog.objects.filter(cat__slug=self.kwargs['cat_slug'], status='published').select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': 'Категорія - ' + str(context['posts'][0].cat), 'cat_selected': context['posts'][0].cat_id}
        context.update(c_def)
        context.update(menu(self.request))
        return context

@login_required
def add_like(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    PostLike.objects.get_or_create(post=post, user=request.user)
    return redirect(post.get_absolute_url())

@login_required
def add_like_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug)
    CommentLike.objects.get_or_create(comment=comment, user=request.user)
    return redirect(comment.post.get_absolute_url())

@login_required
def edit_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(comment.post.get_absolute_url())
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'post': comment.post})

@login_required
def delete_comment(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, user=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect(comment.post.get_absolute_url())
    return render(request, 'delete_comment.html', {'comment': comment})

@login_required
def soon_page(request):
    return render(request, 'soon.html', {'menu': menu(request), 'title': 'Скоро'})

@login_required
def profile(request):
    return render(request, 'profile.html', {'menu': menu(request), 'title': 'Профіль'})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            if hasattr(request.user, 'profile'):
                if 'avatar' in request.FILES:
                    request.user.profile.avatar = request.FILES['avatar']
                    request.user.profile.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form, 'menu': menu(request), 'title': 'Редагувати профіль'})


class UserProfile(DetailView):
    model = CustomUser
    template_name = 'profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user_profile'

def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Сторінку не знайдено</h1>')

@login_required
def add_comment(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'post': post})

@login_required
def edit_post(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    if request.user == post.author or request.user.is_staff:
        if request.method == 'POST':
            form = AddPostForm(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                return redirect(post.get_absolute_url())
        else:
            form = AddPostForm(instance=post)
        return render(request, 'edit_post.html', {'form': form, 'post': post})
    else:
        return redirect('home')

@login_required
@staff_member_required
def delete_post(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'delete_post.html', {'post': post})

def create_blog_view(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            
            send_new_article_notification(blog)

            return redirect('blog_detail', pk=blog.pk)
    else:
        form = BlogForm()

    return render(request, 'create_blog.html', {'form': form})

@login_required
def toggle_like(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    else:
        PostDislike.objects.filter(post=post, user=request.user).delete()
    
    likes_count = post.likes.count()
    dislikes_count = post.dislikes.count()
    
    return JsonResponse({'likes_count': likes_count, 'dislikes_count': dislikes_count})

@login_required
def toggle_dislike(request, post_slug):
    post = get_object_or_404(Blog, slug=post_slug)
    dislike, created = PostDislike.objects.get_or_create(post=post, user=request.user)
    if not created:
        dislike.delete()
    else:
        PostLike.objects.filter(post=post, user=request.user).delete()
    
    likes_count = post.likes.count()
    dislikes_count = post.dislikes.count()
    
    return JsonResponse({'likes_count': likes_count, 'dislikes_count': dislikes_count})

@login_required
def toggle_comment_like(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug)
    like, created_like = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    dislike = CommentDislike.objects.filter(comment=comment, user=request.user).first()

    if dislike:
        dislike.delete()

    if not created_like:
        like.delete()

    comment_likes_count = comment.likes.count()
    comment_dislikes_count = comment.dislikes.count()

    return JsonResponse({'comment_likes_count': comment_likes_count, 'comment_dislikes_count': comment_dislikes_count})

@login_required
def toggle_comment_dislike(request, post_slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug)
    dislike, created_dislike = CommentDislike.objects.get_or_create(comment=comment, user=request.user)
    like = CommentLike.objects.filter(comment=comment, user=request.user).first()

    if like:
        like.delete()

    if not created_dislike:
        dislike.delete()

    comment_likes_count = comment.likes.count()
    comment_dislikes_count = comment.dislikes.count()

    return JsonResponse({'comment_likes_count': comment_likes_count, 'comment_dislikes_count': comment_dislikes_count})

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('home')
    
@login_required
def drafts(request):
    user_drafts = Blog.objects.filter(author=request.user, status='draft')
    return render(request, 'drafts.html', {'drafts': user_drafts, 'title': 'Чернетки'})

@login_required
def edit_draft(request, pk):
    draft = get_object_or_404(Blog, pk=pk, author=request.user, status='draft')

    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES, instance=draft)
        if form.is_valid():
            draft = form.save(commit=False)
            draft.author = request.user
            draft.status = 'published'
            draft.save()
            return redirect('drafts')
        else:
            print(form.errors)
    else:
        form = AddPostForm(instance=draft)

    return render(request, 'edit_draft.html', {'form': form, 'draft': draft})

@login_required
def delete_draft(request, pk):
    draft = get_object_or_404(Blog, pk=pk, status='draft', author=request.user)
    if request.method == 'POST':
        draft.delete()
        return redirect('drafts')  
    return render(request, 'delete_draft.html', {'draft': draft, 'title': 'Видалити чернетку'})


class PostsByTag(ListView):
    model = Blog
    template_name = 'index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Blog.objects.filter(tags__slug=self.kwargs['tag_slug'], status='published').select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Пости з тегом '{self.kwargs['tag_slug']}'"
        context.update(menu(self.request))
        return context