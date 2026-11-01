
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='avatar',
            field=models.URLField(blank=True, default='', verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='admin',
            name='bio',
            field=models.TextField(blank=True, default='', verbose_name='个人简介'),
        ),
        migrations.AddField(
            model_name='admin',
            name='gender',
            field=models.CharField(blank=True, max_length=10, verbose_name='性别'),
        ),
        migrations.AddField(
            model_name='admin',
            name='nick',
            field=models.CharField(blank=True, max_length=50, verbose_name='昵称'),
        ),
        migrations.AddField(
            model_name='admin',
            name='region',
            field=models.CharField(blank=True, max_length=50, verbose_name='地区'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='avatar',
            field=models.URLField(blank=True, default='', verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='bio',
            field=models.TextField(blank=True, default='', verbose_name='个人简介'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='gender',
            field=models.CharField(blank=True, max_length=10, verbose_name='性别'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='nick',
            field=models.CharField(blank=True, max_length=50, verbose_name='昵称'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='region',
            field=models.CharField(blank=True, max_length=50, verbose_name='地区'),
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.URLField(blank=True, default='', verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, default='', verbose_name='个人简介'),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, max_length=10, verbose_name='性别'),
        ),
        migrations.AddField(
            model_name='user',
            name='nick',
            field=models.CharField(blank=True, max_length=50, verbose_name='昵称'),
        ),
        migrations.AddField(
            model_name='user',
            name='region',
            field=models.CharField(blank=True, max_length=50, verbose_name='地区'),
        ),
    ]
