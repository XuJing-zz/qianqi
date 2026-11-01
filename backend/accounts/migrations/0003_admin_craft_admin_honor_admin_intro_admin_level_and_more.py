
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_admin_avatar_admin_bio_admin_gender_admin_nick_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='craft',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='技艺方向'),
        ),
        migrations.AddField(
            model_name='admin',
            name='honor',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='荣誉'),
        ),
        migrations.AddField(
            model_name='admin',
            name='intro',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='一句话签名'),
        ),
        migrations.AddField(
            model_name='admin',
            name='level',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='传承级别'),
        ),
        migrations.AddField(
            model_name='admin',
            name='years',
            field=models.IntegerField(blank=True, null=True, verbose_name='从艺年限'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='craft',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='技艺方向'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='honor',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='荣誉'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='intro',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='一句话签名'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='level',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='传承级别'),
        ),
        migrations.AddField(
            model_name='inheritor',
            name='years',
            field=models.IntegerField(blank=True, null=True, verbose_name='从艺年限'),
        ),
        migrations.AddField(
            model_name='user',
            name='craft',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='技艺方向'),
        ),
        migrations.AddField(
            model_name='user',
            name='honor',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='荣誉'),
        ),
        migrations.AddField(
            model_name='user',
            name='intro',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='一句话签名'),
        ),
        migrations.AddField(
            model_name='user',
            name='level',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='传承级别'),
        ),
        migrations.AddField(
            model_name='user',
            name='years',
            field=models.IntegerField(blank=True, null=True, verbose_name='从艺年限'),
        ),
    ]
