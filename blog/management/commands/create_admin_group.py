from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class Command(BaseCommand):
    help = 'Створення групи "Адміністратори" та призначення дозволів'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Administrators')
        if created:
            custom_user_ct = ContentType.objects.get_for_model(apps.get_model('yourappname', 'CustomUser'))
            permissions = Permission.objects.filter(content_type=custom_user_ct)
            group.permissions.set(permissions)

            blog_ct = ContentType.objects.get_for_model(apps.get_model('yourappname', 'Blog'))
            permissions = Permission.objects.filter(content_type=blog_ct)
            group.permissions.update(permissions)

            category_ct = ContentType.objects.get_for_model(apps.get_model('yourappname', 'Category'))
            permissions = Permission.objects.filter(content_type=category_ct)
            group.permissions.update(permissions)

            comment_ct = ContentType.objects.get_for_model(apps.get_model('yourappname', 'Comment'))
            permissions = Permission.objects.filter(content_type=comment_ct)
            group.permissions.update(permissions)

            self.stdout.write(self.style.SUCCESS("Групу 'Administrators' створено та права додано"))
        else:
            self.stdout.write(self.style.SUCCESS("Групу 'Administrators' вже існує"))
