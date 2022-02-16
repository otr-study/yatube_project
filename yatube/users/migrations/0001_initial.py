# Generated by Django 2.2.19 on 2022-02-15 09:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_pop_article', models.BooleanField(default=True)),
                ('theme', models.CharField(choices=[('light-theme.css', 'Светлая'), ('dark-theme', 'Тёмная')], default='light-theme.css', max_length=100)),
                ('image', models.ImageField(blank=True, upload_to='profiles/', verbose_name='Картинка профиля')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
