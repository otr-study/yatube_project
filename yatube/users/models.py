from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

THEME_CHOICES = (
    ('light-theme.css', 'Светлая'),
    ('dark-theme', 'Тёмная'),
)
PATH_PROFILE_IMAGE = getattr(settings, 'PATH_PROFILE_IMAGE', 'profiles/')


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    use_pop_article = models.BooleanField(
        default=True,
        verbose_name='Отображать популярные записи'
    )
    theme = models.CharField(
        max_length=100,
        choices=THEME_CHOICES,
        default=THEME_CHOICES[0][0],
        verbose_name='Тема'
    )
    image = models.ImageField(
        'Картинка профиля',
        upload_to=PATH_PROFILE_IMAGE,
        blank=True
    )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)
