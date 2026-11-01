
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='学员昵称')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='联系方式')),
                ('avatar_glyph', models.CharField(blank=True, default='学', max_length=10, verbose_name='头像占位字')),
                ('course_id', models.PositiveIntegerField(default=0, verbose_name='课程ID')),
                ('course_name', models.CharField(blank=True, max_length=200, verbose_name='报名课程')),
                ('teacher', models.CharField(blank=True, max_length=50, verbose_name='任课老师')),
                ('craft', models.CharField(blank=True, max_length=50, verbose_name='所属技艺')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='报名费用')),
                ('enroll_time', models.CharField(blank=True, max_length=30, verbose_name='报名时间')),
                ('status', models.CharField(choices=[('ongoing', '进行中'), ('done', '已完成')], default='ongoing', max_length=20, verbose_name='状态')),
                ('progress', models.PositiveIntegerField(default=0, verbose_name='学习进度')),
                ('note', models.TextField(blank=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments', to=settings.AUTH_USER_MODEL, verbose_name='报名用户')),
            ],
            options={
                'verbose_name': '学员',
                'verbose_name_plural': '学员',
                'db_table': 'students_student',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TrainingRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(blank=True, max_length=200, verbose_name='课程名')),
                ('record_time', models.DateTimeField(auto_now_add=True, verbose_name='培训时间')),
                ('content', models.TextField(blank=True, verbose_name='培训内容')),
                ('attendance', models.JSONField(blank=True, default=list, verbose_name='学员出勤表')),
                ('assessment', models.JSONField(blank=True, default=dict, verbose_name='学员考核表')),
                ('remark', models.TextField(blank=True, verbose_name='备注')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='training_records', to='courses.course', verbose_name='课程')),
            ],
            options={
                'verbose_name': '培训记录',
                'verbose_name_plural': '培训记录',
                'db_table': 'training_record',
                'ordering': ['-id'],
            },
        ),
    ]
