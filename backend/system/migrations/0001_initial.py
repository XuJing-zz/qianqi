
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OperationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('login', '登录'), ('create', '新增'), ('update', '修改'), ('delete', '删除'), ('review', '审核'), ('order', '订单'), ('ship', '发货')], default='update', max_length=20, verbose_name='日志类型')),
                ('operator', models.CharField(max_length=50, verbose_name='操作人')),
                ('action', models.CharField(max_length=200, verbose_name='操作')),
                ('detail', models.TextField(blank=True, verbose_name='详情')),
                ('ip', models.CharField(blank=True, default='', max_length=50, verbose_name='操作IP')),
                ('time', models.CharField(blank=True, max_length=30, verbose_name='时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '操作日志',
                'verbose_name_plural': '操作日志',
                'db_table': 'system_operationlog',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True, verbose_name='配置键')),
                ('value', models.JSONField(blank=True, default=dict, verbose_name='配置值')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '系统配置',
                'verbose_name_plural': '系统配置',
                'db_table': 'system_systemconfig',
            },
        ),
    ]
