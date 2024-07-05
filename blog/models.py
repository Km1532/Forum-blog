from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default_avatar.png')

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'username': self.username})

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'Профіль користувача {self.user.username}'

class Blog(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    
    STATUS_CHOICES = [
        (DRAFT, 'Чернетка'),
        (PUBLISHED, 'Опублікована'),
    ]

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name="Текст статті")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото", blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT, verbose_name="Статус")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name="Категорія")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', verbose_name="Автор", null=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True, verbose_name="Лайки", through='PostLike')
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_posts', blank=True, verbose_name="Дизлайки", through='PostDislike')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Запис блогу'
        verbose_name_plural = 'Записи блогу'
        ordering = ['id']

def generate_unique_slug(title):
    slug = slugify(title)
    counter = 1
    while Blog.objects.filter(slug=slug).exists():
        slug = f'{slug}-{counter}'
        counter += 1
    return slug

class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Blog, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class PostDislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Blog, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments', verbose_name="Запис блогу")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Користувач")
    content = models.TextField(verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True, verbose_name="Лайки", through='CommentLike')
    dislikes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='disliked_comments', blank=True, verbose_name="Дизлайки", through='CommentDislike')

    def __str__(self):
        return f'Коментар від {self.user} до {self.post.title}'

    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['created_at']

class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

class CommentDislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['id']

class Draft(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'

    STATUS_CHOICES = [
        (DRAFT, 'Чернетка'),
        (PUBLISHED, 'Опублікована'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    photo = models.ImageField(upload_to='drafts/photos/', blank=True, null=True)
    cat = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категорія", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title