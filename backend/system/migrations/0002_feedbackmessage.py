
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='称呼')),
                ('contact', models.CharField(max_length=100, verbose_name='联系方式')),
                ('subject', models.CharField(blank=True, default='', max_length=100, verbose_name='留言事项')),
                ('message', models.TextField(verbose_name='留言内容')),
                ('status', models.CharField(choices=[('new', '待处理'), ('handled', '已处理')], default='new', max_length=20, verbose_name='状态')),
                ('reply', models.TextField(blank=True, default='', verbose_name='回复')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='提交时间')),
            ],
            options={
                'verbose_name': '联系留言',
                'verbose_name_plural': '联系留言',
                'db_table': 'system_feedbackmessage',
                'ordering': ['-id'],
            },
        ),
    ]
