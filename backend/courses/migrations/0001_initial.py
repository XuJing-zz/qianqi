
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='课程名称')),
                ('craft', models.CharField(blank=True, max_length=50, verbose_name='技艺')),
                ('stage', models.CharField(blank=True, max_length=50, verbose_name='课程阶段')),
                ('difficulty', models.CharField(blank=True, max_length=50, verbose_name='难度')),
                ('duration', models.CharField(blank=True, max_length=50, verbose_name='课时/时长')),
                ('schedule', models.CharField(blank=True, max_length=50, verbose_name='开课时间')),
                ('capacity', models.PositiveIntegerField(default=0, verbose_name='容量')),
                ('price_num', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='价格')),
                ('cover', models.CharField(blank=True, max_length=300, verbose_name='封面图')),
                ('desc', models.TextField(blank=True, verbose_name='课程简介')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回'), ('offline', '已下架')], default='draft', max_length=20, verbose_name='状态')),
                ('enrolled', models.PositiveIntegerField(default=0, verbose_name='已报名人数')),
                ('submit_time', models.CharField(blank=True, max_length=30, verbose_name='提交时间')),
                ('review_comment', models.TextField(blank=True, verbose_name='课程审核意见')),
                ('lessons', models.JSONField(blank=True, default=list, verbose_name='课时')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to='accounts.inheritor', verbose_name='所属传承人')),
            ],
            options={
                'verbose_name': '申报课程',
                'verbose_name_plural': '申报课程',
                'db_table': 'courses_course',
                'ordering': ['-id'],
            },
        ),
    ]
