from django.contrib import admin
from .models import Blog, Category, Comment, CustomUser

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_create', 'photo', 'status')  # Оновлено поле 'is_published' на 'status'
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('status',)  # Оновлено поле 'is_published' на 'status'
    list_filter = ('status', 'time_create')  # Оновлено поле 'is_published' на 'status'
    prepopulated_fields = {"slug": ("title",)}

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    list_display_links = ('id', 'post')
    search_fields = ('post__title', 'user__username', 'content')

admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
