
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeritageProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='姓名')),
                ('gender', models.CharField(blank=True, default='男', max_length=10, verbose_name='性别')),
                ('age', models.PositiveIntegerField(default=0, verbose_name='年龄')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='联系方式')),
                ('mentor', models.CharField(blank=True, max_length=100, verbose_name='师承关系')),
                ('years', models.PositiveIntegerField(default=0, verbose_name='从艺年限')),
                ('level', models.CharField(blank=True, max_length=20, verbose_name='传承等级')),
                ('craft', models.CharField(blank=True, max_length=100, verbose_name='代表技艺')),
                ('honors', models.TextField(blank=True, verbose_name='所获荣誉')),
                ('intro', models.TextField(blank=True, verbose_name='个人简介')),
                ('qual', models.CharField(blank=True, max_length=100, verbose_name='教学资质')),
                ('status', models.CharField(choices=[('active', '在职'), ('leave', '离岗')], default='active', max_length=20, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('account', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='heritage_profile', to='accounts.inheritor', verbose_name='关联账号')),
            ],
            options={
                'verbose_name': '传承人',
                'verbose_name_plural': '传承人',
                'db_table': 'heritage_profile',
            },
        ),
    ]
