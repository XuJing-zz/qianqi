
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='技艺名称')),
                ('glyph', models.CharField(blank=True, default='技', max_length=10, verbose_name='图标字')),
                ('level', models.CharField(blank=True, max_length=20, verbose_name='技艺级别')),
                ('category', models.CharField(blank=True, max_length=50, verbose_name='技艺分类')),
                ('region', models.CharField(blank=True, max_length=50, verbose_name='所在地区')),
                ('origin', models.CharField(blank=True, max_length=100, verbose_name='发源地')),
                ('abstract', models.TextField(blank=True, verbose_name='技艺概述')),
                ('years', models.PositiveIntegerField(default=0, verbose_name='从艺年限')),
                ('desc', models.TextField(blank=True, verbose_name='技艺简介')),
                ('steps', models.TextField(blank=True, verbose_name='工序步骤(｜分隔)')),
                ('works', models.TextField(blank=True, verbose_name='代表作品(｜分隔)')),
                ('courses', models.TextField(blank=True, verbose_name='关联课程(｜分隔)')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回'), ('offline', '已下架')], default='draft', max_length=20, verbose_name='状态')),
                ('submit_time', models.CharField(blank=True, max_length=30, verbose_name='提交时间')),
                ('review_comment', models.TextField(blank=True, verbose_name='审核意见')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='skills', to='accounts.inheritor', verbose_name='所属传承人')),
            ],
            options={
                'verbose_name': '技艺档案',
                'verbose_name_plural': '技艺档案',
                'db_table': 'skills_skill',
                'ordering': ['-id'],
            },
        ),
    ]
